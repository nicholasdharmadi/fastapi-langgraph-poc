"""Lead schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LeadBase(BaseModel):
    """Base lead schema."""
    name: str
    phone: str
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead."""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for lead response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

