from fastapi import APIRouter, Depends, HTTPException, Body, status
from pydantic import BaseModel
import logging

from app.services import notification_service # Absolute import
# Import dependencies if needed (e.g., for auth)
# from ...db.session import get_db
# from .users import get_current_user
# from ... import models

logger = logging.getLogger(__name__)

router = APIRouter()

# Input schema
class SlackTestInput(BaseModel):
    message: str = "This is a test message from JobBright!"

# Output schema
class SlackTestOutput(BaseModel):
    success: bool
    detail: str

@router.post(
    "/send-test-slack", 
    response_model=SlackTestOutput,
    summary="Send Test Slack Message",
    description="Sends a predefined or custom test message to the configured Slack webhook.",
    tags=["notifications"] # Add a tag for grouping in docs
)
async def send_test_slack_message_endpoint(
    # Add dependencies like current_user if this needs to be protected
    # current_user: models.User = Depends(get_current_user),
    input_data: SlackTestInput = Body(...) # Get data from request body
):
    """
    Endpoint to trigger sending a test Slack message.
    """
    logger.info(f"Received request to send test Slack message: '{input_data.message}'")
    success = notification_service.send_slack_message(input_data.message)
    
    if success:
        return SlackTestOutput(success=True, detail="Test Slack message sent successfully.")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to send test Slack message. Check logs and SLACK_WEBHOOK_URL configuration."
        )

# Add other notification-related endpoints here