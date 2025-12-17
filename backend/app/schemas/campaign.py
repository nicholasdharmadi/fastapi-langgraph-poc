"""Campaign schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from app.models.campaign import CampaignStatus, AgentType

if TYPE_CHECKING:
    from app.schemas.campaign_lead import CampaignLeadResponse


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str
    description: Optional[str] = None
    agent_type: AgentType = AgentType.SMS
    sms_system_prompt: Optional[str] = None
    sms_temperature: int = 70
    workflow_config: Optional[Dict[str, Any]] = None
    
    # Legacy single agent (backward compatible)
    agent_id: Optional[int] = None
    
    # A2A dual agents
    creative_agent_id: Optional[int] = None
    deterministic_agent_id: Optional[int] = None


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    lead_ids: Optional[List[int]] = None  # Optional list of lead IDs to assign
    lead_count: Optional[int] = None  # Or auto-assign N random leads
    phone_numbers: Optional[List[str]] = None  # List of phone numbers to target (will create/find leads)


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[AgentType] = None
    sms_system_prompt: Optional[str] = None
    sms_temperature: Optional[int] = None
    status: Optional[CampaignStatus] = None
    
    # Legacy single agent
    agent_id: Optional[int] = None
    
    # A2A dual agents
    creative_agent_id: Optional[int] = None
    deterministic_agent_id: Optional[int] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response."""
    id: int
    status: CampaignStatus
    stats: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CampaignWithLeads(CampaignResponse):
    """Schema for campaign response with leads."""
    campaign_leads: List[Dict[str, Any]] = []  # Simplified to avoid circular import
    
    model_config = ConfigDict(from_attributes=True)

