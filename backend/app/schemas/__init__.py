"""Pydantic schemas for request/response validation."""
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignWithLeads,
)
from app.schemas.campaign_lead import CampaignLeadResponse
from app.schemas.processing_log import ProcessingLogResponse

__all__ = [
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignWithLeads",
    "CampaignLeadResponse",
    "ProcessingLogResponse",
]

