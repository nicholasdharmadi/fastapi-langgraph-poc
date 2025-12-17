"""ProcessingLog model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ProcessingLog(Base):
    """ProcessingLog model for tracking campaign lead processing."""
    
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_lead_id = Column(Integer, ForeignKey("campaign_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Log details
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    node_name = Column(String(100), nullable=True)  # LangGraph node name
    message = Column(Text, nullable=False)
    log_metadata = Column(JSON, nullable=True)  # Additional structured data (renamed from metadata)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign_lead = relationship("CampaignLead", back_populates="processing_logs")
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, level='{self.level}', node='{self.node_name}')>"

