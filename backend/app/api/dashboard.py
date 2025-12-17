"""Dashboard API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Campaign, Lead, CampaignLead
from app.models.campaign import CampaignStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    
    # Campaign stats
    total_campaigns = db.query(func.count(Campaign.id)).scalar()
    active_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.status == CampaignStatus.PROCESSING
    ).scalar()
    completed_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.status == CampaignStatus.COMPLETED
    ).scalar()
    
    # Lead stats
    total_leads = db.query(func.count(Lead.id)).scalar()
    
    # Campaign lead stats
    total_campaign_leads = db.query(func.count(CampaignLead.id)).scalar()
    sms_sent = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.sms_sent == True
    ).scalar()
    completed_leads = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.status == 'completed'
    ).scalar()
    failed_leads = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.status == 'failed'
    ).scalar()
    
    # Success rate
    success_rate = (completed_leads / total_campaign_leads * 100) if total_campaign_leads > 0 else 0
    
    return {
        "campaigns": {
            "total": total_campaigns,
            "active": active_campaigns,
            "completed": completed_campaigns
        },
        "leads": {
            "total": total_leads,
            "in_campaigns": total_campaign_leads,
            "sms_sent": sms_sent,
            "completed": completed_leads,
            "failed": failed_leads,
            "success_rate": round(success_rate, 2)
        }
    }


@router.get("/recent-campaigns")
def get_recent_campaigns(limit: int = 5, db: Session = Depends(get_db)):
    """Get recent campaigns."""
    campaigns = db.query(Campaign).order_by(
        Campaign.created_at.desc()
    ).limit(limit).all()
    
    return campaigns

