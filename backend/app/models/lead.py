"""Lead model."""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Lead(Base):
    """Lead model for storing contact information."""
    
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign_leads = relationship("CampaignLead", back_populates="lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', phone='{self.phone}')>"

