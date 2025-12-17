"""API endpoints for prompt builder / recording analysis."""
import os
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil
import asyncio

from app.database import get_db
from app.models.recording import Recording, Transcript, Analysis, GeneratedPrompt, RecordingStatus
from app.schemas.recording import (
    RecordingResponse,
    RecordingDetailResponse,
    GeneratedPromptResponse,
    GeneratedPromptUpdate,
    ProcessingStatusResponse
)
from app.tasks.recording_processor import process_recording_task
from app.services.prompt_chat import PromptChatService
from app.schemas.prompt_chat import ChatSessionResponse, ChatMessageCreate, ChatMessageResponse, SavePromptRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["prompt-builder"])

# Upload directory
UPLOAD_DIR = Path("/Users/nicholas/Desktop/NMG/fastapi-langgraph-poc/backend/uploads/recordings")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/recordings/upload", response_model=RecordingResponse)
async def upload_recording(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a sales call recording for analysis.
    
    Accepts audio files in common formats (mp3, wav, m4a, etc.)
    """
    try:
        # Validate file type
        allowed_extensions = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Create recording record
        recording = Recording(
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            status=RecordingStatus.UPLOADED,
            recording_metadata={
                "original_filename": file.filename,
                "content_type": file.content_type
            }
        )
        
        db.add(recording)
        db.commit()
        db.refresh(recording)
        
        # Queue background processing
        # Note: Using asyncio.create_task instead of RQ for simplicity
        # In production, use RQ worker
        asyncio.create_task(process_recording_async(recording.id, db))
        
        logger.info(f"Uploaded recording {recording.id}: {file.filename}")
        
        return recording
        
    except Exception as e:
        logger.error(f"Error uploading recording: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_recording_async(recording_id: int, db: Session):
    """Wrapper to process recording in background."""
    try:
        await process_recording_task(recording_id, db)
    except Exception as e:
        logger.error(f"Background processing failed for recording {recording_id}: {str(e)}")


@router.get("/recordings", response_model=List[RecordingResponse])
def list_recordings(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all recordings."""
    recordings = db.query(Recording).order_by(Recording.created_at.desc()).offset(skip).limit(limit).all()
    return recordings


@router.get("/recordings/{recording_id}", response_model=RecordingDetailResponse)
def get_recording(
    recording_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed recording information including transcript, analysis, and prompts."""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return recording


@router.get("/recordings/{recording_id}/status", response_model=ProcessingStatusResponse)
def get_processing_status(
    recording_id: int,
    db: Session = Depends(get_db)
):
    """Get the current processing status of a recording."""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Calculate progress
    progress_map = {
        RecordingStatus.UPLOADED: 10.0,
        RecordingStatus.TRANSCRIBING: 30.0,
        RecordingStatus.ANALYZING: 60.0,
        RecordingStatus.COMPLETED: 100.0,
        RecordingStatus.FAILED: 0.0
    }
    
    step_map = {
        RecordingStatus.UPLOADED: "Queued for processing",
        RecordingStatus.TRANSCRIBING: "Transcribing audio",
        RecordingStatus.ANALYZING: "Analyzing conversation",
        RecordingStatus.COMPLETED: "Complete",
        RecordingStatus.FAILED: "Failed"
    }
    
    return ProcessingStatusResponse(
        recording_id=recording.id,
        status=recording.status,
        progress=progress_map.get(recording.status, 0.0),
        current_step=step_map.get(recording.status, "Unknown"),
        error_message=recording.error_message
    )


@router.delete("/recordings/{recording_id}")
def delete_recording(
    recording_id: int,
    db: Session = Depends(get_db)
):
    """Delete a recording and all associated data."""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Delete file
    try:
        file_path = Path(recording.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Could not delete file {recording.file_path}: {str(e)}")
    
    # Delete database record (cascade will handle related records)
    db.delete(recording)
    db.commit()
    
    return {"message": "Recording deleted successfully"}


@router.get("/prompts/{prompt_id}", response_model=GeneratedPromptResponse)
def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific generated prompt."""
    prompt = db.query(GeneratedPrompt).filter(GeneratedPrompt.id == prompt_id).first()
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return prompt


@router.patch("/prompts/{prompt_id}", response_model=GeneratedPromptResponse)
def update_prompt(
    prompt_id: int,
    updates: GeneratedPromptUpdate,
    db: Session = Depends(get_db)
):
    """Update a generated prompt (e.g., edit text, change settings, mark as active)."""
    prompt = db.query(GeneratedPrompt).filter(GeneratedPrompt.id == prompt_id).first()
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Apply updates
    if updates.prompt_text is not None:
        prompt.prompt_text = updates.prompt_text
    
    if updates.voice_settings is not None:
        prompt.voice_settings = updates.voice_settings
    
    if updates.llm_config is not None:
        prompt.llm_config = updates.llm_config
    
    if updates.is_active is not None:
        # If setting this prompt as active, deactivate others for same recording
        if updates.is_active:
            db.query(GeneratedPrompt).filter(
                GeneratedPrompt.recording_id == prompt.recording_id,
                GeneratedPrompt.id != prompt.id
            ).update({"is_active": 0})
        
        prompt.is_active = 1 if updates.is_active else 0
    
    if updates.performance_metrics is not None:
        prompt.performance_metrics = updates.performance_metrics
    
    db.commit()
    db.refresh(prompt)
    
    return prompt


@router.post("/prompts/{prompt_id}/regenerate", response_model=GeneratedPromptResponse)
async def regenerate_prompt(
    prompt_id: int,
    feedback: str = None,
    db: Session = Depends(get_db)
):
    """Regenerate a prompt with optional feedback."""
    prompt = db.query(GeneratedPrompt).filter(GeneratedPrompt.id == prompt_id).first()
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Get recording data
    recording = db.query(Recording).filter(Recording.id == prompt.recording_id).first()
    transcript = db.query(Transcript).filter(Transcript.recording_id == prompt.recording_id).first()
    analysis = db.query(Analysis).filter(Analysis.recording_id == prompt.recording_id).first()
    
    if not transcript or not analysis:
        raise HTTPException(status_code=400, detail="Recording not fully processed")
    
    # Generate new prompt
    from app.services.prompt_generator import PromptGeneratorService
    prompt_service = PromptGeneratorService()
    
    if feedback:
        # Refine based on feedback
        new_prompt_text = await prompt_service.refine_prompt(prompt.prompt_text, feedback)
    else:
        # Regenerate from scratch
        analysis_data = {
            "tonality_description": analysis.tonality_description,
            "communication_style": analysis.communication_style,
            "hooks": analysis.hooks,
            "objections": analysis.objections,
            "key_phrases": analysis.key_phrases,
            "conversation_flow": analysis.conversation_flow,
            "success_patterns": analysis.success_patterns,
            "voice_profile": analysis.voice_profile
        }
        new_prompt_text = await prompt_service.generate_system_prompt(
            transcript.full_text,
            analysis_data
        )
    
    # Create new version
    max_version = db.query(GeneratedPrompt).filter(
        GeneratedPrompt.recording_id == prompt.recording_id
    ).count()
    
    new_prompt = GeneratedPrompt(
        recording_id=prompt.recording_id,
        prompt_text=new_prompt_text,
        version=max_version + 1,
        voice_settings=prompt.voice_settings,
        llm_config=prompt.llm_config,
        is_active=0
    )
    
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    return new_prompt


@router.post("/chat/start", response_model=ChatSessionResponse)
async def start_chat_session(db: Session = Depends(get_db)):
    """Start a new interactive prompt building session."""
    service = PromptChatService(db)
    return await service.create_session()


@router.post("/chat/{session_id}/message", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: int, 
    message: ChatMessageCreate, 
    db: Session = Depends(get_db)
):
    """Send a message to the chat session."""
    service = PromptChatService(db)
    return await service.add_message(session_id, message.content)


@router.post("/chat/{session_id}/message/stream")
async def send_chat_message_stream(
    session_id: int, 
    message: ChatMessageCreate, 
    db: Session = Depends(get_db)
):
    """Send a message to the chat session with streaming response."""
    from fastapi.responses import StreamingResponse
    service = PromptChatService(db)
    return StreamingResponse(
        service.add_message_stream(session_id, message.content),
        media_type="text/event-stream"
    )



@router.post("/chat/{session_id}/save", response_model=GeneratedPromptResponse)
def save_chat_prompt(
    session_id: int,
    request: SavePromptRequest,
    db: Session = Depends(get_db)
):
    """Save the current draft prompt without regeneration."""
    service = PromptChatService(db)
    return service.save_prompt(session_id, request.draft_prompt, request.name)


@router.post("/chat/{session_id}/finalize", response_model=GeneratedPromptResponse)
async def finalize_chat_session(
    session_id: int, 
    db: Session = Depends(get_db)
):
    """Finalize the chat session and generate the system prompt."""
    service = PromptChatService(db)
    return await service.generate_final_prompt(session_id)


@router.get("/prompts/library", response_model=List[GeneratedPromptResponse])
def get_saved_prompts(db: Session = Depends(get_db)):
    """Get all saved prompts from both recordings and chat sessions."""
    prompts = db.query(GeneratedPrompt).order_by(GeneratedPrompt.created_at.desc()).all()
    return prompts
