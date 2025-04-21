import requests
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

def send_slack_message(message: str) -> bool:
    """
    Sends a message to the configured Slack webhook URL.

    Args:
        message: The text message to send.

    Returns:
        True if the message was sent successfully (status code 2xx), False otherwise.
    """
    if not settings.SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not configured. Cannot send Slack message.")
        return False

    payload = {"text": message}
    
    try:
        response = requests.post(settings.SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        logger.info(f"Successfully sent Slack message: '{message[:50]}...'")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Slack message: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred sending Slack message: {e}", exc_info=True)
        return False