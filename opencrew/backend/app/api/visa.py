from fastapi import APIRouter, Depends, HTTPException
import uuid
from typing import List, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app import schemas # Import schemas
from app.models.user import User # Import User model specifically
from app.services import visa_alerts # Absolute import
from app.db.session import get_db # Absolute import
from app.api.users import get_current_active_user # Absolute import from correct module
from app.core.security import get_current_supabase_user_id # Import Supabase user ID dependency

router = APIRouter()


# Define Enum for status matching frontend
class VisaStatusEnum(str, Enum):
    INFO = "Info"
    ACTION_REQUIRED = "Action Required"
    UPCOMING_DEADLINE = "Upcoming Deadline"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    UNKNOWN = "Unknown"

# Define Pydantic schema for the response item matching frontend
class VisaTimelineItem(BaseModel):
    id: Union[str, int]
    date: str # Using string for now to match mock data format
    title: str
    description: str | None = None
    status: VisaStatusEnum

# Mock data (adapted from frontend, replace with DB logic later)
# Using static dates for predictability in mock data
MOCK_VISA_DATA: List[VisaTimelineItem] = [
    VisaTimelineItem(id=1, date="2025-04-22", title="I-765 Submitted", description="OPT application sent.", status=VisaStatusEnum.SUBMITTED),
    VisaTimelineItem(id=2, date="2025-04-20", title="Passport Scan Requested", description="Upload required by ISSS.", status=VisaStatusEnum.ACTION_REQUIRED),
    VisaTimelineItem(id=3, date="2025-04-15", title="Visa Interview Scheduled", description="Appointment confirmed for next month.", status=VisaStatusEnum.INFO),
    VisaTimelineItem(id=4, date="2025-04-08", title="SEVIS Fee Paid", description="Confirmation received.", status=VisaStatusEnum.INFO),
    VisaTimelineItem(id=5, date="2025-04-21", title="I-20 Received", description="Document received from university.", status=VisaStatusEnum.INFO),
    VisaTimelineItem(id=6, date="2025-04-23", title="Check RFE Status", description="Potential Request for Evidence.", status=VisaStatusEnum.UPCOMING_DEADLINE),
]

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



# --- New Endpoint ---
@router.get(
    "/timeline",
    response_model=List[VisaTimelineItem],
    summary="Get Visa Application Timeline",
    description="Retrieves the visa application timeline steps for the authenticated user (currently uses placeholder data)."
)
async def get_visa_timeline(
    current_user_id: uuid.UUID = Depends(get_current_supabase_user_id) # Protect route
):
    """
    Retrieves the visa application timeline for the authenticated user.
    TODO: Replace mock data with actual database query based on user_id.
    """
    print(f"Backend: Fetching visa timeline for user ID: {current_user_id}")
    # Return mock data for now
    return MOCK_VISA_DATA
