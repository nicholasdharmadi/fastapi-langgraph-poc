"""Campaign model."""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CampaignStatus(str, enum.Enum):
    """Campaign status enum."""
    DRAFT = "draft"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentType(str, enum.Enum):
    """Agent type enum."""
    SMS = "sms"
    VOICE = "voice"
    BOTH = "both"


class Campaign(Base):
    """Campaign model for managing outreach campaigns."""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(SQLEnum(AgentType), nullable=False, default=AgentType.SMS)
    status = Column(SQLEnum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)
    
    # SMS Configuration
    sms_system_prompt = Column(Text, nullable=True)
    sms_temperature = Column(Integer, nullable=False, default=70)  # 0-100, will be divided by 100
    workflow_config = Column(JSON, nullable=True)
    
    # Statistics (JSON field for flexibility)
    stats = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    campaign_leads = relationship("CampaignLead", back_populates="campaign", cascade="all, delete-orphan")
    
    # Legacy single agent (for backward compatibility)
    from sqlalchemy import ForeignKey
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    agent = relationship("Agent", back_populates="campaigns", foreign_keys=[agent_id])
    
    # A2A Architecture: Dual agent support
    creative_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    deterministic_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    creative_agent = relationship(
        "Agent", 
        back_populates="creative_campaigns",
        foreign_keys=[creative_agent_id]
    )
    deterministic_agent = relationship(
        "Agent", 
        back_populates="deterministic_campaigns",
        foreign_keys=[deterministic_agent_id]
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def update_stats(self):
        """Update campaign statistics based on campaign leads."""
        total = len(self.campaign_leads)
        pending = sum(1 for cl in self.campaign_leads if cl.status == "pending")
        processing = sum(1 for cl in self.campaign_leads if cl.status == "processing")
        completed = sum(1 for cl in self.campaign_leads if cl.status == "completed")
        failed = sum(1 for cl in self.campaign_leads if cl.status == "failed")
        sms_sent = sum(1 for cl in self.campaign_leads if cl.sms_sent)
        
        self.stats = {
            "total_leads": total,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed,
            "sms_sent": sms_sent,
            "success_rate": (completed / total * 100) if total > 0 else 0,
        }

