"""Agent schemas."""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.agent import AgentRole

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    model: str = "gpt-4o"
    role: AgentRole = AgentRole.HYBRID  # A2A: creative, deterministic, or hybrid
    capabilities: List[str] = []
    tools: List[Dict[str, Any]] = []

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    role: Optional[AgentRole] = None  # A2A: Allow updating role
    capabilities: Optional[List[str]] = None
    tools: Optional[List[Dict[str, Any]]] = None

class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
