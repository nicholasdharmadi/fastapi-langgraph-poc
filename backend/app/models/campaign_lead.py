"""CampaignLead model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CampaignLead(Base):
    """CampaignLead model linking campaigns to leads with processing status."""
    
    __tablename__ = "campaign_leads"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Processing status
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    
    # Results
    sms_sent = Column(Boolean, default=False)
    sms_message = Column(Text, nullable=True)
    sms_response = Column(Text, nullable=True)
    voice_call_made = Column(Boolean, default=False)
    
    # Tracing
    trace_id = Column(String(255), nullable=True)  # LangSmith trace ID
    error_message = Column(Text, nullable=True)
    
    # Manual mode for human takeover
    manual_mode = Column(Boolean, default=False)  # When True, AI won't auto-respond
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_leads")
    lead = relationship("Lead", back_populates="campaign_leads")
    processing_logs = relationship("ProcessingLog", back_populates="campaign_lead", cascade="all, delete-orphan")
    conversation_messages = relationship("ConversationMessage", back_populates="campaign_lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CampaignLead(id={self.id}, campaign_id={self.campaign_id}, lead_id={self.lead_id}, status='{self.status}')>"

