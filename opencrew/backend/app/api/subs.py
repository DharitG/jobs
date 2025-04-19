import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session
import stripe # Import stripe library

from .. import crud, models, schemas
from ..core import security # Assuming security module handles user auth
from ..db.session import get_db
from ..core.config import settings # Import settings for API keys

logger = logging.getLogger(__name__)
router = APIRouter()

# Configure Stripe API key from settings
# Ensure STRIPE_SECRET_KEY is defined in your core.config.settings object
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
else:
    logger.warning("Stripe secret key not configured. Stripe API calls will fail.")

# TODO: Define STRIPE_WEBHOOK_SECRET in settings for webhook verification
# endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

@router.post("/create-checkout-session", response_model=schemas.StripeCheckoutSession) # Correctly references the schema now
async def create_checkout_session(
    # Define request body schema later (e.g., price ID)
    # checkout_request: schemas.CheckoutRequest, # Add request schema later
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user) # Assuming this dependency gets the authenticated user
):
    """
    Creates a Stripe Checkout session for the user to subscribe.
    """
    logger.info(f"User {current_user.id} requesting checkout session.")
    # --- TODO: Implement Stripe Checkout Session Creation ---
    # 1. Get Price ID from request body or determine based on user action.
    # 2. Use stripe.checkout.Session.create(...)
    #    - Provide price ID, customer email (or create/retrieve Stripe customer ID)
    #    - Set success_url and cancel_url
    #    - Set mode='subscription'
    # 3. Return the session ID or URL to the frontend.

    # Placeholder response - returning schema instance
    return schemas.StripeCheckoutSession(
        session_id="cs_test_placeholder_session_id",
        url="https://checkout.stripe.com/pay/cs_test_placeholder"
    )


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming webhooks from Stripe to update subscription status, etc.
    """
    logger.info("Received Stripe webhook.")
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET # Get secret from settings

    # --- TODO: Implement Stripe Webhook Verification and Handling ---

    # --- TODO: Implement Stripe Webhook Verification and Handling ---
    # 1. Verify the webhook signature using stripe.Webhook.construct_event(...)
    #    - Pass payload, sig_header, endpoint_secret
    # 2. Handle specific event types (e.g., 'checkout.session.completed', 'customer.subscription.updated', 'customer.subscription.deleted')
    #    - If 'checkout.session.completed':
    #        - Retrieve session details.
    #        - Get user identifier (e.g., from client_reference_id or metadata).
    #        - Update user's subscription status, tier, Stripe customer ID, subscription ID in your DB.
    #    - If 'customer.subscription.updated'/'deleted':
    #        - Retrieve subscription details.
    #        - Update user's subscription status/tier in your DB based on the event.
    # 3. Return 200 OK to Stripe quickly.

    try:
        # Verify the webhook signature using stripe.Webhook.construct_event(...)
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        logger.info(f"Stripe webhook event received and verified: {event['type']}")

        # Handle event based on event['type']
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # TODO: Handle successful checkout
            # - Get user identifier (e.g., client_reference_id or metadata)
            # - Update user subscription status in DB
            logger.info(f"Checkout session completed: {session.get('id')}")
            pass # Add handling logic here
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            # TODO: Handle subscription updates (e.g., plan change, cancellation)
            # - Update user subscription status in DB
            logger.info(f"Subscription updated: {subscription.get('id')}, Status: {subscription.get('status')}")
            pass # Add handling logic here
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            # TODO: Handle subscription cancellations
            # - Update user subscription status in DB
            logger.info(f"Subscription deleted: {subscription.get('id')}")
            pass # Add handling logic here
        else:
            logger.info(f"Unhandled Stripe event type: {event['type']}")

    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe webhook payload: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe webhook signature: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing error")

    return {"status": "success"}

# Add more subscription management endpoints if needed (e.g., cancel, update payment method via Stripe Billing Portal)
