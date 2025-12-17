"""Campaign API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Campaign, Lead, CampaignLead, ProcessingLog
from app.models.campaign import CampaignStatus
from app.schemas import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignWithLeads
from app.tasks.campaign_tasks import enqueue_campaign_processing

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=List[CampaignResponse])
@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all campaigns."""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignWithLeads)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get a specific campaign with leads."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Manually convert campaign_leads to dict to avoid serialization issues
    campaign_dict = {
        "id": campaign.id,
        "name": campaign.name,
        "description": campaign.description,
        "agent_type": campaign.agent_type,
        "status": campaign.status,
        "agent_id": campaign.agent_id,
        "sms_system_prompt": campaign.sms_system_prompt,
        "sms_temperature": campaign.sms_temperature,
        "stats": campaign.stats,
        "created_at": campaign.created_at,
        "updated_at": campaign.updated_at,
        "started_at": campaign.started_at,
        "completed_at": campaign.completed_at,
        "campaign_leads": [
            {
                "id": cl.id,
                "campaign_id": cl.campaign_id,
                "lead_id": cl.lead_id,
                "status": cl.status,
                "sms_sent": cl.sms_sent,
                "sms_message": cl.sms_message,
                "sms_response": cl.sms_response,
                "voice_call_made": cl.voice_call_made,
                "trace_id": cl.trace_id,
                "error_message": cl.error_message,
                "created_at": cl.created_at,
                "updated_at": cl.updated_at,
                "processed_at": cl.processed_at,
                "lead": {
                    "id": cl.lead.id,
                    "name": cl.lead.name,
                    "phone": cl.lead.phone,
                    "email": cl.lead.email,
                    "company": cl.lead.company,
                } if cl.lead else None
            }
            for cl in campaign.campaign_leads
        ]
    }
    return campaign_dict


@router.post("", response_model=CampaignResponse, status_code=201)
@router.post("/", response_model=CampaignResponse, status_code=201)
def create_campaign(campaign_data: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new campaign."""
    # Create campaign
    campaign_dict = campaign_data.model_dump(exclude={'lead_ids', 'lead_count', 'phone_numbers'})
    campaign = Campaign(**campaign_dict)
    campaign.stats = {}
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Assign leads
    # Assign leads
    leads = []
    
    if campaign_data.lead_ids:
        # Assign specific leads
        leads.extend(db.query(Lead).filter(Lead.id.in_(campaign_data.lead_ids)).all())
        
    if campaign_data.lead_count:
        # Assign random leads
        leads.extend(db.query(Lead).order_by(func.random()).limit(campaign_data.lead_count).all())
        
    if campaign_data.phone_numbers:
        # Find or create leads from phone numbers
        for phone in campaign_data.phone_numbers:
            # Check if lead exists
            lead = db.query(Lead).filter(Lead.phone == phone).first()
            if not lead:
                # Create new lead
                lead = Lead(name=f"Lead {phone}", phone=phone)
                db.add(lead)
                db.commit()
                db.refresh(lead)
            leads.append(lead)
            
    # Deduplicate leads
    leads = list({l.id: l for l in leads}.values())
    
    # Create CampaignLead records
    for lead in leads:
        campaign_lead = CampaignLead(
            campaign_id=campaign.id,
            lead_id=lead.id,
            status='pending'
        )
        db.add(campaign_lead)
    
    db.commit()
    
    # Update stats
    campaign.update_stats()
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: int, campaign_data: CampaignUpdate, db: Session = Depends(get_db)):
    """Update a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=204)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db.delete(campaign)
    db.commit()
    return None


@router.post("/{campaign_id}/start")
def start_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Start processing a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.PENDING]:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign cannot be started from status: {campaign.status}"
        )
    
    # Update status to pending
    campaign.status = CampaignStatus.PENDING
    db.commit()
    
    # Enqueue background task
    job_id = enqueue_campaign_processing(campaign_id)
    
    return {
        "message": "Campaign processing started",
        "campaign_id": campaign_id,
        "job_id": job_id
    }


@router.get("/{campaign_id}/logs")
def get_campaign_logs(campaign_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get processing logs for a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    logs = db.query(ProcessingLog).join(CampaignLead).filter(
        CampaignLead.campaign_id == campaign_id
    ).order_by(ProcessingLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return logs


@router.post("/{campaign_id}/pause")
def pause_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Pause a running campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.PROCESSING:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign cannot be paused from status: {campaign.status}"
        )
    
    campaign.status = CampaignStatus.PAUSED
    db.commit()
    
    return {"message": "Campaign paused", "campaign_id": campaign_id}


@router.post("/{campaign_id}/resume")
def resume_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Resume a paused campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign cannot be resumed from status: {campaign.status}"
        )
    
    # Update status back to processing
    campaign.status = CampaignStatus.PROCESSING
    db.commit()
    
    # Re-enqueue background task to pick up where it left off
    # The task logic handles skipping already completed leads
    job_id = enqueue_campaign_processing(campaign_id)
    
    return {
        "message": "Campaign resumed",
        "campaign_id": campaign_id,
        "job_id": job_id
    }

