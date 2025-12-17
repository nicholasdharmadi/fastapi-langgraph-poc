"""API endpoints for conversation and trace management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import CampaignLead, ConversationMessage
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationMessageResponse(BaseModel):
    id: int
    campaign_lead_id: int
    role: str
    content: str
    message_metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationMessageCreate(BaseModel):
    role: str
    content: str
    message_metadata: Optional[dict] = None


@router.get("/campaign-lead/{campaign_lead_id}", response_model=List[ConversationMessageResponse])
def get_conversation_by_campaign_lead(
    campaign_lead_id: int,
    db: Session = Depends(get_db)
):
    """Get all conversation messages for a specific campaign lead."""
    campaign_lead = db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Campaign lead not found")
    
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.campaign_lead_id == campaign_lead_id
    ).order_by(ConversationMessage.created_at.asc()).all()
    
    return messages


@router.post("/campaign-lead/{campaign_lead_id}", response_model=ConversationMessageResponse)
def create_conversation_message(
    campaign_lead_id: int,
    message: ConversationMessageCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation message."""
    campaign_lead = db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Campaign lead not found")
    
    db_message = ConversationMessage(
        campaign_lead_id=campaign_lead_id,
        role=message.role,
        content=message.content,
        message_metadata=message.message_metadata
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.get("/lead/{lead_id}", response_model=List[ConversationMessageResponse])
def get_conversations_by_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get all conversation messages across all campaigns for a specific lead."""
    messages = db.query(ConversationMessage).join(CampaignLead).filter(
        CampaignLead.lead_id == lead_id
    ).order_by(ConversationMessage.created_at.desc()).all()
    
    return messages


class ManualModeToggle(BaseModel):
    manual_mode: bool


@router.post("/campaign-lead/{campaign_lead_id}/toggle-manual-mode")
def toggle_manual_mode(
    campaign_lead_id: int,
    toggle: ManualModeToggle,
    db: Session = Depends(get_db)
):
    """Toggle manual mode for a campaign lead conversation."""
    campaign_lead = db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Campaign lead not found")
    
    campaign_lead.manual_mode = toggle.manual_mode
    db.commit()
    db.refresh(campaign_lead)
    
    return {
        "campaign_lead_id": campaign_lead_id,
        "manual_mode": campaign_lead.manual_mode,
        "message": f"Manual mode {'enabled' if toggle.manual_mode else 'disabled'}"
    }


class ManualMessageRequest(BaseModel):
    message: str


@router.post("/campaign-lead/{campaign_lead_id}/send-manual-message")
def send_manual_message(
    campaign_lead_id: int,
    request: ManualMessageRequest,
    db: Session = Depends(get_db)
):
    """Send a manual message from human agent to lead."""
    from app.services.sms_service import SMSService
    from app.models import Lead
    
    campaign_lead = db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()
    if not campaign_lead:
        raise HTTPException(status_code=404, detail="Campaign lead not found")
    
    lead = db.query(Lead).filter(Lead.id == campaign_lead.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Send SMS via Twilio
    sms_service = SMSService()
    result = sms_service.send_sms(
        to=lead.phone,
        message=request.message
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {result.get('error')}")
    
    # Log the message in conversation history
    db_message = ConversationMessage(
        campaign_lead_id=campaign_lead_id,
        role='assistant',  # Human agent message sent as assistant
        content=request.message,
        message_metadata={
            'manual': True,
            'message_id': result.get('message_id'),
            'sent_at': datetime.now().isoformat()
        }
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return {
        "success": True,
        "message_id": result.get('message_id'),
        "conversation_message_id": db_message.id,
        "message": "Manual message sent successfully"
    }

