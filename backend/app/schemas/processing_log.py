"""ProcessingLog schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ProcessingLogResponse(BaseModel):
    """Schema for processing log response."""
    id: int
    campaign_lead_id: int
    level: str
    node_name: Optional[str] = None
    message: str
    log_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

