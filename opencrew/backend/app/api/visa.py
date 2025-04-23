from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app import schemas # Import schemas
from app.models.user import User # Import User model specifically
from app.services import visa_alerts # Absolute import
from app.db.session import get_db # Absolute import
from app.core.security import get_current_active_user # Absolute import (Note: different function than other APIs)

router = APIRouter()

# Define a simple response model for now
# In a real app, you'd likely use Pydantic schemas matching the data structure
VisaUpdateResponse = List[Dict[str, Any]]

@router.get(
    "/updates",
    response_model=VisaUpdateResponse,
    summary="Get Recent Visa Updates",
    description="Fetches recent visa-related news and updates (currently uses placeholder data)."
)
async def get_visa_updates(
    days: int = 7, # Allow specifying history length, default to 7
    current_user: User = Depends(get_current_active_user) # Use imported User type
):
    """
    Retrieves recent visa updates for the authenticated user.
    """
    try:
        updates = visa_alerts.get_recent_visa_updates(days=days)
        return updates
    except Exception as e:
        # Log the exception details if needed
        # logger.error(f"Error fetching visa updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch visa updates.")

# Placeholder for future endpoints like lawyer chat initiation
# @router.post("/lawyer-chat/request", ...)
# async def request_lawyer_chat(...):
#    ...
