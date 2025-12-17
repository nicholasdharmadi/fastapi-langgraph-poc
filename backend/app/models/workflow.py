"""Workflow model."""
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Workflow(Base):
    """Workflow model for saved campaign workflows."""
    
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)  # Stores nodes and edges
    is_template = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}')>"
