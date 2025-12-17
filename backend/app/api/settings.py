"""Settings API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.config import settings
import os

router = APIRouter(prefix="/settings", tags=["settings"])


class WorkingHoursSettings(BaseModel):
    """Working hours configuration."""
    enforce_working_hours: bool
    working_hours_start: int
    working_hours_end: int
    allow_weekend_sending: bool


class WorkingHoursResponse(WorkingHoursSettings):
    """Working hours response with current time info."""
    current_hour: int
    current_day: str
    is_currently_allowed: bool


@router.get("/working-hours", response_model=WorkingHoursResponse)
def get_working_hours():
    """Get current working hours configuration."""
    from datetime import datetime
    
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Check if sending is currently allowed
    is_allowed = True
    if settings.ENFORCE_WORKING_HOURS:
        # Check weekend
        if not settings.ALLOW_WEEKEND_SENDING and current_weekday >= 5:
            is_allowed = False
        # Check hours
        if not (settings.WORKING_HOURS_START <= current_hour < settings.WORKING_HOURS_END):
            is_allowed = False
    
    return {
        "enforce_working_hours": settings.ENFORCE_WORKING_HOURS,
        "working_hours_start": settings.WORKING_HOURS_START,
        "working_hours_end": settings.WORKING_HOURS_END,
        "allow_weekend_sending": settings.ALLOW_WEEKEND_SENDING,
        "current_hour": current_hour,
        "current_day": day_names[current_weekday],
        "is_currently_allowed": is_allowed
    }


@router.put("/working-hours", response_model=WorkingHoursResponse)
def update_working_hours(config: WorkingHoursSettings):
    """
    Update working hours configuration.
    
    NOTE: This only updates in-memory settings for the current session.
    To persist changes, update the .env file and restart containers.
    """
    from datetime import datetime
    
    # Validate hours
    if not (0 <= config.working_hours_start <= 23):
        raise ValueError("working_hours_start must be between 0 and 23")
    if not (1 <= config.working_hours_end <= 24):
        raise ValueError("working_hours_end must be between 1 and 24")
    if config.working_hours_start >= config.working_hours_end:
        raise ValueError("working_hours_start must be less than working_hours_end")
    
    # Update settings (in-memory only)
    settings.ENFORCE_WORKING_HOURS = config.enforce_working_hours
    settings.WORKING_HOURS_START = config.working_hours_start
    settings.WORKING_HOURS_END = config.working_hours_end
    settings.ALLOW_WEEKEND_SENDING = config.allow_weekend_sending
    
    # Return updated settings with current status
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    is_allowed = True
    if settings.ENFORCE_WORKING_HOURS:
        if not settings.ALLOW_WEEKEND_SENDING and current_weekday >= 5:
            is_allowed = False
        if not (settings.WORKING_HOURS_START <= current_hour < settings.WORKING_HOURS_END):
            is_allowed = False
    
    return {
        "enforce_working_hours": settings.ENFORCE_WORKING_HOURS,
        "working_hours_start": settings.WORKING_HOURS_START,
        "working_hours_end": settings.WORKING_HOURS_END,
        "allow_weekend_sending": settings.ALLOW_WEEKEND_SENDING,
        "current_hour": current_hour,
        "current_day": day_names[current_weekday],
        "is_currently_allowed": is_allowed
    }

