"""Agent model."""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AgentRole(str, enum.Enum):
    """Agent role for A2A architecture."""
    CREATIVE = "creative"  # Handles conversation, message generation, context
    DETERMINISTIC = "deterministic"  # Handles tool calling, API integrations, structured ops
    HYBRID = "hybrid"  # Can handle both (for backward compatibility)


class Agent(Base):
    """Agent model for defining AI assistants."""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    model = Column(String(50), nullable=False, default="gpt-4o")
    
    # A2A Architecture: Role of this agent
    role = Column(SQLEnum(AgentRole), nullable=False, default=AgentRole.HYBRID)
    
    # Capabilities (e.g., ["sms", "voice"])
    capabilities = Column(JSON, nullable=False, default=[])
    
    # Tools configuration (e.g., [{"name": "calendly", "config": {...}}])
    tools = Column(JSON, nullable=False, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaigns = relationship(
        "Campaign", 
        back_populates="agent",
        foreign_keys="Campaign.agent_id"
    )
    
    # A2A Relationships
    creative_campaigns = relationship(
        "Campaign", 
        back_populates="creative_agent",
        foreign_keys="Campaign.creative_agent_id"
    )
    deterministic_campaigns = relationship(
        "Campaign", 
        back_populates="deterministic_agent",
        foreign_keys="Campaign.deterministic_agent_id"
    )

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', role='{self.role}')>"
