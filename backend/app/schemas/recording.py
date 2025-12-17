"""Pydantic schemas for recording/prompt builder feature."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.recording import RecordingStatus


# Recording Schemas
class RecordingBase(BaseModel):
    """Base recording schema."""
    filename: str
    recording_metadata: Optional[Dict[str, Any]] = None


class RecordingCreate(RecordingBase):
    """Schema for creating a recording."""
    pass


class RecordingResponse(RecordingBase):
    """Schema for recording response."""
    id: int
    file_path: str
    file_size: int
    duration: Optional[float] = None
    status: RecordingStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Transcript Schemas
class TranscriptBase(BaseModel):
    """Base transcript schema."""
    full_text: str
    speaker_segments: Optional[List[Dict[str, Any]]] = None


class TranscriptCreate(TranscriptBase):
    """Schema for creating a transcript."""
    recording_id: int
    elevenlabs_transcript_id: Optional[str] = None
    confidence_score: Optional[float] = None


class TranscriptResponse(TranscriptBase):
    """Schema for transcript response."""
    id: int
    recording_id: int
    elevenlabs_transcript_id: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisBase(BaseModel):
    """Base analysis schema."""
    tonality_description: Optional[str] = None
    communication_style: Optional[Dict[str, Any]] = None
    hooks: Optional[List[Dict[str, Any]]] = None
    objections: Optional[List[Dict[str, Any]]] = None
    key_phrases: Optional[List[str]] = None
    conversation_flow: Optional[Dict[str, Any]] = None
    success_patterns: Optional[Dict[str, Any]] = None
    voice_profile: Optional[Dict[str, Any]] = None
    recommended_voice_id: Optional[str] = None


class AnalysisCreate(AnalysisBase):
    """Schema for creating an analysis."""
    recording_id: int


class AnalysisResponse(AnalysisBase):
    """Schema for analysis response."""
    id: int
    recording_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Generated Prompt Schemas
class GeneratedPromptBase(BaseModel):
    """Base generated prompt schema."""
    prompt_text: str
    voice_settings: Optional[Dict[str, Any]] = None
    llm_config: Optional[Dict[str, Any]] = None


class GeneratedPromptCreate(GeneratedPromptBase):
    """Schema for creating a generated prompt."""
    recording_id: int
    version: int = 1


class GeneratedPromptUpdate(BaseModel):
    """Schema for updating a generated prompt."""
    prompt_text: Optional[str] = None
    voice_settings: Optional[Dict[str, Any]] = None
    llm_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class GeneratedPromptResponse(GeneratedPromptBase):
    """Schema for generated prompt response."""
    id: int
    recording_id: Optional[int] = None
    prompt_chat_session_id: Optional[int] = None
    source_type: str
    name: Optional[str] = None
    version: int
    performance_metrics: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Combined Response Schemas
class RecordingDetailResponse(RecordingResponse):
    """Detailed recording response with related data."""
    transcript: Optional[TranscriptResponse] = None
    analysis: Optional[AnalysisResponse] = None
    prompts: List[GeneratedPromptResponse] = []
    
    class Config:
        from_attributes = True


class ProcessingStatusResponse(BaseModel):
    """Response for processing status."""
    recording_id: int
    status: RecordingStatus
    progress: float = Field(..., ge=0.0, le=100.0)
    current_step: str
    error_message: Optional[str] = None
