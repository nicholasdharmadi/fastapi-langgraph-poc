"""Background tasks for processing recordings."""
import logging
from sqlalchemy.orm import Session
from app.models.recording import Recording, Transcript, Analysis, GeneratedPrompt, RecordingStatus
from app.services.elevenlabs import ElevenLabsService
from app.services.analysis import AnalysisService
from app.services.prompt_generator import PromptGeneratorService

logger = logging.getLogger(__name__)


async def process_recording_task(recording_id: int, db: Session):
    """
    Background task to process a recording.
    
    Steps:
    1. Transcribe audio
    2. Analyze transcript
    3. Generate system prompt
    
    Args:
        recording_id: ID of the recording to process
        db: Database session
    """
    try:
        # Get recording
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            logger.error(f"Recording {recording_id} not found")
            return
        
        # Update status
        recording.status = RecordingStatus.TRANSCRIBING
        db.commit()
        
        # Step 1: Transcribe
        logger.info(f"Transcribing recording {recording_id}")
        elevenlabs = ElevenLabsService()
        transcript_data = await elevenlabs.transcribe_audio(recording.file_path)
        
        # Save transcript
        transcript = Transcript(
            recording_id=recording_id,
            full_text=transcript_data["full_text"],
            speaker_segments=transcript_data.get("segments", []),
            confidence_score=transcript_data.get("confidence", None)
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        # Update recording duration if available
        if transcript_data.get("duration"):
            recording.duration = transcript_data["duration"]
        
        # Step 2: Analyze
        logger.info(f"Analyzing recording {recording_id}")
        recording.status = RecordingStatus.ANALYZING
        db.commit()
        
        analysis_service = AnalysisService()
        analysis_data = await analysis_service.analyze_transcript(
            transcript.full_text,
            transcript.speaker_segments or []
        )
        
        # Save analysis
        analysis = Analysis(
            recording_id=recording_id,
            tonality_description=analysis_data.get("tonality_description"),
            communication_style=analysis_data.get("communication_style"),
            hooks=analysis_data.get("hooks"),
            objections=analysis_data.get("objections"),
            key_phrases=analysis_data.get("key_phrases"),
            conversation_flow=analysis_data.get("conversation_flow"),
            success_patterns=analysis_data.get("success_patterns"),
            voice_profile=analysis_data.get("voice_profile"),
            recommended_voice_id=analysis_data.get("recommended_voice_id")
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Step 3: Generate prompt
        logger.info(f"Generating prompt for recording {recording_id}")
        prompt_service = PromptGeneratorService()
        prompt_text = await prompt_service.generate_system_prompt(
            transcript.full_text,
            analysis_data
        )
        
        # Save generated prompt
        voice_settings = analysis_data.get("voice_profile", {}).get("recommended_settings", {})
        generated_prompt = GeneratedPrompt(
            recording_id=recording_id,
            prompt_text=prompt_text,
            version=1,
            voice_settings=voice_settings,
            llm_config={
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500
            },
            is_active=1  # Make it active by default
        )
        db.add(generated_prompt)
        
        # Update recording status
        recording.status = RecordingStatus.COMPLETED
        db.commit()
        
        logger.info(f"Successfully processed recording {recording_id}")
        
    except Exception as e:
        logger.error(f"Error processing recording {recording_id}: {str(e)}")
        
        # Update recording with error
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if recording:
            recording.status = RecordingStatus.FAILED
            recording.error_message = str(e)
            db.commit()
        
        raise
