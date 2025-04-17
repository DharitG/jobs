import logging

from .celery_app import celery_app # Import the configured Celery app
from ..services import autosubmit

logger = logging.getLogger(__name__)

@celery_app.task(acks_late=True, name="tasks.trigger_auto_apply") # Use explicit name
def trigger_auto_apply(application_id: int):
    """Celery task to trigger the auto-application process for a given application ID."""
    logger.info(f"Received task trigger_auto_apply for application_id: {application_id}")
    try:
        # Call the actual auto-submit function from the service
        autosubmit.apply_to_job(application_id=application_id)
        logger.info(f"Successfully processed task trigger_auto_apply for application_id: {application_id}")
        # The result/status update should happen within apply_to_job or via another mechanism
    except Exception as e:
        # Log the error; Celery can handle retries based on configuration if needed
        logger.error(f"Error processing task trigger_auto_apply for application_id: {application_id}. Error: {e}", exc_info=True)
        # Depending on retry policy, this might raise the exception to trigger a retry
        raise

# Add other tasks here later, e.g.:
# @celery_app.task(name="tasks.send_email")
# def send_email_task(recipient: str, subject: str, body: str):
#     from ..services import emailer # Import here to avoid circular dependencies
#     emailer.send_email(to=recipient, subject=subject, body=body) 