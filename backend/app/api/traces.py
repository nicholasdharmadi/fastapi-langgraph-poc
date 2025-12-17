"""API endpoints for LangSmith trace management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Campaign, CampaignLead
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/traces", tags=["traces"])


class TraceInfoResponse(BaseModel):
    """Response model for trace information."""
    trace_id: Optional[str]
    langsmith_url: Optional[str]
    campaign_lead_id: int
    status: str
    created_at: datetime
    processed_at: Optional[datetime]


@router.get("/campaign/{campaign_id}")
def get_campaign_traces(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get all trace IDs for a campaign with LangSmith URLs."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign_leads = db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign_id
    ).all()
    
    traces = []
    for cl in campaign_leads:
        trace_info = {
            "trace_id": cl.trace_id,
            "langsmith_url": f"https://smith.langchain.com/o/your-org/projects/p/your-project/r/{cl.trace_id}" if cl.trace_id else None,
            "campaign_lead_id": cl.id,
            "lead_id": cl.lead_id,
            "lead_name": cl.lead.name if cl.lead else None,
            "status": cl.status,
            "created_at": cl.created_at,
            "processed_at": cl.processed_at
        }
        traces.append(trace_info)
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "total_traces": len(traces),
        "traces": traces
    }


@router.get("/campaign-lead/{campaign_lead_id}")
def get_campaign_lead_trace(
    campaign_lead_id: int,
    db: Session = Depends(get_db)
):
    """Get trace information for a specific campaign lead."""
    campaign_lead = db.query(CampaignLead).filter(
        CampaignLead.id == campaign_lead_id
    ).first()
    
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Campaign lead not found")
    
    return {
        "campaign_lead_id": campaign_lead.id,
        "trace_id": campaign_lead.trace_id,
        "langsmith_url": f"https://smith.langchain.com/o/your-org/projects/p/your-project/r/{campaign_lead.trace_id}" if campaign_lead.trace_id else None,
        "status": campaign_lead.status,
        "lead": {
            "id": campaign_lead.lead.id,
            "name": campaign_lead.lead.name,
            "phone": campaign_lead.lead.phone
        } if campaign_lead.lead else None,
        "campaign": {
            "id": campaign_lead.campaign.id,
            "name": campaign_lead.campaign.name
        } if campaign_lead.campaign else None,
        "created_at": campaign_lead.created_at,
        "processed_at": campaign_lead.processed_at,
        "error_message": campaign_lead.error_message
    }
