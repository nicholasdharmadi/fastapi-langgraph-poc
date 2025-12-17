"""Workflow schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    is_template: bool = False

class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow."""
    pass

class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_template: Optional[bool] = None

class WorkflowResponse(WorkflowBase):
    """Schema for workflow response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
