"""Campaign Lead API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CampaignLead
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/campaign-leads", tags=["campaign-leads"])


class LeadInfo(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CampaignLeadDetail(BaseModel):
    id: int
    campaign_id: int
    lead_id: int
    status: str
    manual_mode: bool
    sms_sent: bool
    sms_message: Optional[str] = None
    sms_response: Optional[str] = None
    voice_call_made: bool
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    lead: LeadInfo
    campaign: CampaignInfo

    class Config:
        from_attributes = True


@router.get("/{campaign_lead_id}", response_model=CampaignLeadDetail)
def get_campaign_lead(
    campaign_lead_id: int,
    db: Session = Depends(get_db)
):
    """Get campaign lead details with lead and campaign info."""
    campaign_lead = db.query(CampaignLead).filter(
        CampaignLead.id == campaign_lead_id
    ).first()
    
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Campaign lead not found")
    
    return campaign_lead
