"""Conversation message model for tracking agent-lead interactions."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ConversationMessage(Base):
    """ConversationMessage model for storing conversation history."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_lead_id = Column(
        Integer, 
        ForeignKey("campaign_leads.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Message details
    role = Column(String(50), nullable=False)  # 'system', 'assistant', 'user', 'tool'
    content = Column(Text, nullable=False)
    
    # Additional context (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    message_metadata = Column(JSON, nullable=True)  # Store node name, step info, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign_lead = relationship("CampaignLead", back_populates="conversation_messages")
    
    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, campaign_lead_id={self.campaign_lead_id}, role='{self.role}')>"
