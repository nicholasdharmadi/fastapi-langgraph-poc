"""Recording model for prompt builder feature."""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RecordingStatus(str, enum.Enum):
    """Status of recording processing."""
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Recording(Base):
    """Recording model for storing uploaded sales call recordings."""
    
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    duration = Column(Float, nullable=True)  # in seconds
    status = Column(SQLEnum(RecordingStatus), nullable=False, default=RecordingStatus.UPLOADED)
    
    # Metadata
    recording_metadata = Column(JSON, nullable=True)  # format, sample_rate, etc.
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transcript = relationship("Transcript", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    analysis = relationship("Analysis", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    prompts = relationship("GeneratedPrompt", back_populates="recording", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recording(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class Transcript(Base):
    """Transcript model for storing transcribed text from recordings."""
    
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False, index=True)
    
    # Transcript content
    full_text = Column(Text, nullable=False)
    speaker_segments = Column(JSON, nullable=True)  # [{speaker: "A", text: "...", start: 0.0, end: 5.2}]
    
    # ElevenLabs specific data
    elevenlabs_transcript_id = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recording = relationship("Recording", back_populates="transcript")
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, recording_id={self.recording_id})>"


class Analysis(Base):
    """Analysis model for storing extracted insights from recordings."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False, index=True)
    
    # Tonality & Style
    tonality_description = Column(Text, nullable=True)
    communication_style = Column(JSON, nullable=True)  # {formality: "casual", energy: "high", pace: "moderate"}
    
    # Content Analysis
    hooks = Column(JSON, nullable=True)  # [{text: "...", timestamp: 12.5, effectiveness: "high"}]
    objections = Column(JSON, nullable=True)  # [{objection: "...", response: "...", outcome: "resolved"}]
    key_phrases = Column(JSON, nullable=True)  # ["phrase1", "phrase2"]
    
    # Conversation Structure
    conversation_flow = Column(JSON, nullable=True)  # {opening: {...}, discovery: {...}, closing: {...}}
    success_patterns = Column(JSON, nullable=True)
    
    # Voice Characteristics (for TTS)
    voice_profile = Column(JSON, nullable=True)  # {pitch: "medium", speed: 1.2, emphasis_patterns: [...]}
    recommended_voice_id = Column(String(255), nullable=True)  # ElevenLabs voice ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recording = relationship("Recording", back_populates="analysis")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, recording_id={self.recording_id})>"



class PromptSourceType(str, enum.Enum):
    """Source of the generated prompt."""
    RECORDING = "recording"
    CHAT = "chat"


class PromptChatSession(Base):
    """Chat session for interactive prompt building."""
    
    __tablename__ = "prompt_chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Chat State
    messages = Column(JSON, nullable=False, default=[])  # List of {role: str, content: str}
    current_step = Column(String(50), nullable=True)  # e.g., "personality", "tone", "tools"
    is_completed = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prompts = relationship("GeneratedPrompt", back_populates="chat_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PromptChatSession(id={self.id}, steps={len(self.messages)})>"


class GeneratedPrompt(Base):
    """Generated prompt model for storing AI-generated system prompts."""
    
    __tablename__ = "generated_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source (Poly-morphic relationship)
    source_type = Column(SQLEnum(PromptSourceType), nullable=False, default=PromptSourceType.RECORDING)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=True, index=True)
    prompt_chat_session_id = Column(Integer, ForeignKey("prompt_chat_sessions.id"), nullable=True, index=True)
    
    # Prompt content
    prompt_text = Column(Text, nullable=False)
    name = Column(String(255), nullable=True)  # User-friendly name for the prompt
    version = Column(Integer, nullable=False, default=1)
    
    # Configuration
    voice_settings = Column(JSON, nullable=True)  # ElevenLabs voice settings
    llm_config = Column(JSON, nullable=True)  # temperature, max_tokens, etc.
    
    # Performance tracking
    performance_metrics = Column(JSON, nullable=True)  # {conversion_rate: 0.0, avg_call_duration: 0.0}
    is_active = Column(Integer, nullable=False, default=0)  # Boolean as int
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recording = relationship("Recording", back_populates="prompts")
    chat_session = relationship("PromptChatSession", back_populates="prompts")
    
    def __repr__(self):
        return f"<GeneratedPrompt(id={self.id}, source={self.source_type}, version={self.version})>"
