"""CampaignLead schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class CampaignLeadResponse(BaseModel):
    """Schema for campaign lead response."""
    id: int
    campaign_id: int
    lead_id: int
    status: str
    sms_sent: bool
    sms_message: Optional[str] = None
    sms_response: Optional[str] = None
    voice_call_made: bool
    trace_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Include lead details
    lead: Optional[Any] = None
    
    model_config = ConfigDict(from_attributes=True)

