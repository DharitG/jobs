from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..models.user import SubscriptionTier # Import the enum

# Shared properties
class UserBase(BaseModel):
    auth0_sub: str # Added Auth0 Subject ID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None # Keep for potential display/legacy use
    phone_number: str | None = None
    linkedin_url: str | None = None

# Properties to receive via API on creation (Now likely handled by Auth0 flow, but schema might be used internally)
class UserCreate(UserBase):
    # password: str # Removed for Auth0
    pass # Keep structure, might be used for internal creation if needed

# Properties to receive via API on update (e.g., profile update, or internal updates via webhook)
class UserUpdate(BaseModel):
    # password: str | None = None # Removed for Auth0
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None # Keep for potential display/legacy use
    phone_number: str | None = None
    linkedin_url: str | None = None
    is_active: bool | None = None # Activation status
    
    # Add Stripe subscription fields for updates (likely triggered by webhooks)
    subscription_tier: SubscriptionTier | None = None
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    stripe_subscription_status: str | None = None # e.g., 'active', 'canceled' from Stripe
    subscription_current_period_end: datetime | None = None

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    is_active: bool
    subscription_tier: SubscriptionTier # Add tier here
    current_streak: int # Added for daily streak
    last_streak_update: datetime | None = None # Added for daily streak

    class Config:
        from_attributes = True # Pydantic V2 uses this instead of orm_mode

# Properties to return to client
class User(UserInDBBase):
    pass # Inherits all from UserInDBBase

# Properties stored in DB (includes fields not usually returned to client)
class UserInDB(UserInDBBase):
    # hashed_password: str # Removed for Auth0
    pass # Currently no DB-only fields beyond UserInDBBase after removing password
