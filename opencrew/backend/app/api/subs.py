import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session
import stripe # Import stripe library

import os # Need os for FRONTEND_BASE_URL placeholder
from app import crud # Import crud only
from app.schemas.payment import StripeCheckoutSession # Import payment schema directly
from app.models.user import User, SubscriptionTier # Import User and Enum
from app.schemas.payment import CheckoutRequest # Absolute import
from app.schemas.user import UserUpdate # Absolute import
# Remove incorrect security import for user dependency
from app.api.users import get_current_active_user # Import the correct user dependency function
from app.db.session import get_db # Absolute import
from app.core.config import settings # Absolute import

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

@router.post("/create-checkout-session", response_model=StripeCheckoutSession) # Use direct import
async def create_checkout_session(
    checkout_request: CheckoutRequest, # Use the input schema
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Use the correctly imported dependency
):
    """
    Creates a Stripe Checkout session for the user to subscribe.
    """
    logger.info(f"User {current_user.id} requesting checkout session for price_id: {checkout_request.price_id}.")
    
    if not stripe.api_key:
        logger.error("Stripe API key is not configured.")
        raise HTTPException(status_code=500, detail="Stripe integration is not configured.")

    # Define placeholder URLs - **ADJUST THESE TO YOUR ACTUAL FRONTEND ROUTES**
    # These URLs must be absolute or relative to your frontend base URL
    # Example assumes frontend is hosted separately and base URL is known or configured
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000") # Example: Get from env
    success_url = f"{FRONTEND_BASE_URL}/dashboard?checkout=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{FRONTEND_BASE_URL}/pricing?checkout=cancel"

    try:
        # Check if user already has a Stripe customer ID, create if not
        stripe_customer_id = current_user.stripe_customer_id
        if not stripe_customer_id:
             # Consider creating the customer here, or checking if they exist by email
             # customer = stripe.Customer.create(email=current_user.email, name=f"{current_user.first_name} {current_user.last_name}")
             # stripe_customer_id = customer.id
             # # TODO: Save the stripe_customer_id back to the user model in DB
             # crud.user.update_user(db, db_obj=current_user, obj_in={"stripe_customer_id": stripe_customer_id})
             logger.info(f"User {current_user.id} does not have a Stripe customer ID yet. Proceeding without existing customer.")
             # Alternatively, you can pass the email directly to the session create call if you haven't created customers yet
             customer_creation_params = {"email": current_user.email}
        else:
             logger.info(f"Using existing Stripe customer ID for user {current_user.id}: {stripe_customer_id}")
             customer_creation_params = {"customer": stripe_customer_id}


        checkout_session = stripe.checkout.Session.create(
            # customer=stripe_customer_id, # Use if you have the customer ID
            **customer_creation_params, # Pass either customer email or customer ID
            line_items=[
                {
                    'price': checkout_request.price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            # Pass user ID for webhook handling
            client_reference_id=str(current_user.id),
             # Optionally add metadata if needed
            # metadata={
            #     'user_id': current_user.id
            # }
        )
        
        logger.info(f"Created Stripe checkout session {checkout_session.id} for user {current_user.id}")

        return StripeCheckoutSession( # Use direct import
            session_id=checkout_session.id,
            url=checkout_session.url # Return the actual checkout URL
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error creating checkout session for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not create checkout session: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error creating checkout session for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error creating checkout session.")


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
            logger.info(f"Processing checkout.session.completed for session: {session.get('id')}")

            # --- Get User ID from session ---
            user_id_str = session.get('client_reference_id')
            if not user_id_str:
                logger.error(f"Missing client_reference_id in checkout session {session.get('id')}")
                # Potentially lookup user by customer email if needed as fallback
                # raise HTTPException(status_code=400, detail="Missing user identifier in session.")
                return {"status": "error", "detail": "Missing user identifier"} # Return 200 to Stripe, but log error

            try:
                user_id = int(user_id_str)
            except ValueError:
                 logger.error(f"Invalid client_reference_id (not an int): {user_id_str} in session {session.get('id')}")
                 return {"status": "error", "detail": "Invalid user identifier"}

            # --- Fetch User ---
            db_user = crud.user.get_user(db, user_id=user_id)
            if not db_user:
                logger.error(f"User not found for ID: {user_id} from session {session.get('id')}")
                return {"status": "error", "detail": "User not found"}

            # --- Extract Stripe Info ---
            stripe_customer_id = session.get('customer')
            stripe_subscription_id = session.get('subscription')

            if not stripe_customer_id or not stripe_subscription_id:
                 logger.error(f"Missing customer or subscription ID in session {session.get('id')} for user {user_id}")
                 return {"status": "error", "detail": "Missing Stripe IDs"}

            # --- Determine Subscription Tier ---
            # We need to map the Price ID from the checkout session
            # back to our internal SubscriptionTier enum.

            # --- Tier Mapping Logic ---
            new_tier = SubscriptionTier.FREE # Default to FREE if lookup fails (Use imported Enum)
            import json # Make sure json is imported for tier_map parsing

            try:
                # Retrieve the line items from the session
                line_items = stripe.checkout.Session.list_line_items(session.id, limit=1) # Requires stripe import
                if line_items and line_items.data:
                    price_id = line_items.data[0].price.id
                    logger.info(f"Found price_id '{price_id}' in checkout session {session.id}")
                    
                    # Parse the mapping from config JSON string
                    tier_map = json.loads(settings.STRIPE_PRICE_ID_TIER_MAP_JSON)
                    tier_name = tier_map.get(price_id)
                    
                    if tier_name:
                        new_tier = SubscriptionTier(tier_name) # Convert string to enum (Use imported Enum)
                        logger.info(f"Mapped price_id '{price_id}' to tier '{new_tier}' for user {user_id}.")
                    else:
                         logger.error(f"Could not map price_id '{price_id}' to a known tier for user {user_id}. Check STRIPE_PRICE_ID_TIER_MAP_JSON config.")
                         # Keep default FREE tier or handle error differently?
                else:
                     logger.error(f"Could not retrieve line items for session {session.id}. Cannot determine tier.")
            except json.JSONDecodeError:
                 logger.error(f"Failed to parse STRIPE_PRICE_ID_TIER_MAP_JSON. Ensure it's valid JSON. Raw value: '{settings.STRIPE_PRICE_ID_TIER_MAP_JSON}'")
            except ValueError as e: # Handles invalid tier name during enum conversion
                logger.error(f"Invalid tier name '{tier_name}' found in mapping for price_id '{price_id}': {e}")
            except stripe.error.StripeError as e:
                 logger.error(f"Stripe API error fetching line items for session {session.id}: {e}")
            except Exception as e:
                 logger.exception(f"Unexpected error during tier mapping for session {session.id}: {e}")
            # --- End Tier Mapping Logic ---

            # --- Prepare User Update ---
            user_update_data = UserUpdate(
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                subscription_tier=new_tier,
                stripe_subscription_status='active' # Assume active on checkout completion
                # Optionally fetch subscription details to get current_period_end
                # sub_details = stripe.Subscription.retrieve(stripe_subscription_id)
                # subscription_current_period_end=datetime.fromtimestamp(sub_details.current_period_end)
            )

            # --- Update User in DB ---
            try:
                updated_user = crud.user.update_user(db=db, db_user=db_user, user_in=user_update_data)
                logger.info(f"Successfully updated user {updated_user.id} subscription to {updated_user.subscription_tier} via webhook.")
            except Exception as db_error:
                 logger.error(f"Failed to update user {user_id} in DB after checkout {session.get('id')}: {db_error}", exc_info=True)
                 # Decide if we should retry or raise an error that Stripe might see (returning 500)
                 # Returning 200 but logging is often preferred to avoid Stripe retries if DB issue is temporary
                 return {"status": "error", "detail": "Database update failed"}

        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            logger.info(f"Processing customer.subscription.updated for sub: {subscription.get('id')}, Status: {subscription.get('status')}")
            
            stripe_customer_id = subscription.get('customer')
            stripe_subscription_id = subscription.get('id')
            new_status = subscription.get('status') # e.g., "active", "past_due", "canceled", "unpaid"
            
            # Determine the tier from the price ID (important if plan changes)
            new_tier = SubscriptionTier.FREE # Default (Use imported Enum)
            import json # Make sure json is imported

            try:
                if subscription.items and subscription.items.data:
                    price_id = subscription.items.data[0].price.id
                    tier_map = json.loads(settings.STRIPE_PRICE_ID_TIER_MAP_JSON)
                    tier_name = tier_map.get(price_id)
                    if tier_name:
                        new_tier = SubscriptionTier(tier_name) # Use imported Enum
                    else:
                        logger.warning(f"Subscription update: Could not map price_id '{price_id}' to tier for sub {stripe_subscription_id}.")
                else:
                     logger.warning(f"Subscription update: No items found for sub {stripe_subscription_id}, cannot determine tier from price.")
            except Exception as e:
                 logger.exception(f"Subscription update: Error mapping tier for sub {stripe_subscription_id}: {e}")

            # Get period end
            current_period_end = None
            if subscription.get('current_period_end'):
                 try:
                     # Import datetime if not already imported at top
                     from datetime import datetime, timezone
                     current_period_end = datetime.fromtimestamp(subscription.get('current_period_end'), tz=timezone.utc)
                 except Exception as date_e:
                      logger.error(f"Error converting period end timestamp for sub {stripe_subscription_id}: {date_e}")

            # Find user by customer ID (assuming customer ID is reliably stored)
            # Alternatively, query based on subscription ID if stored uniquely
            db_user = db.query(User).filter(User.stripe_customer_id == stripe_customer_id).first() # Use imported User
            if not db_user:
                 logger.error(f"Subscription update: User not found for Stripe Customer ID: {stripe_customer_id}, Sub ID: {stripe_subscription_id}")
                 return {"status": "error", "detail": "User not found for customer ID"}

            # Prepare update
            user_update_data = UserUpdate(
                stripe_subscription_id=stripe_subscription_id, # Ensure this is stored if changed/missing
                subscription_tier=new_tier,
                stripe_subscription_status=new_status,
                subscription_current_period_end=current_period_end
            )

            # Update User in DB
            try:
                updated_user = crud.user.update_user(db=db, db_user=db_user, user_in=user_update_data)
                logger.info(f"Successfully updated user {updated_user.id} subscription status to '{new_status}' for sub {stripe_subscription_id}.")
            except Exception as db_error:
                 logger.error(f"Failed to update user {db_user.id} subscription status via webhook for sub {stripe_subscription_id}: {db_error}", exc_info=True)
                 return {"status": "error", "detail": "Database update failed"}

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Processing customer.subscription.deleted for sub: {subscription.get('id')}")
            
            stripe_customer_id = subscription.get('customer')
            stripe_subscription_id = subscription.get('id') # Get ID for logging/lookup if needed

            # Find user by customer ID
            db_user = db.query(User).filter(User.stripe_customer_id == stripe_customer_id).first() # Use imported User
            if not db_user:
                 # Alternatively, lookup by subscription ID if that's reliably stored and unique
                 # db_user = db.query(models.User).filter(models.User.stripe_subscription_id == stripe_subscription_id).first()
                 logger.error(f"Subscription deleted: User not found for Stripe Customer ID: {stripe_customer_id}, Sub ID: {stripe_subscription_id}")
                 return {"status": "error", "detail": "User not found for customer ID"}
                 
            # Prepare update - Revert to Free tier, clear Stripe info
            user_update_data = UserUpdate(
                subscription_tier=SubscriptionTier.FREE, # Use imported Enum
                stripe_subscription_status='canceled', # Or 'deleted', depending on desired state representation
                stripe_subscription_id=None, # Clear the subscription ID
                subscription_current_period_end=None # Clear the period end
            )

            # Update User in DB
            try:
                updated_user = crud.user.update_user(db=db, db_user=db_user, user_in=user_update_data)
                logger.info(f"Successfully reverted user {updated_user.id} to FREE tier due to subscription deletion (Sub ID: {stripe_subscription_id}).")
            except Exception as db_error:
                 logger.error(f"Failed to revert user {db_user.id} to FREE tier after subscription deletion {stripe_subscription_id}: {db_error}", exc_info=True)
                 return {"status": "error", "detail": "Database update failed"}

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
