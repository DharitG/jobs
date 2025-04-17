from pydantic import BaseModel, EmailStr

from ..models.user import SubscriptionTier # Import the enum

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update (optional)
class UserUpdate(BaseModel):
    password: str | None = None
    full_name: str | None = None
    # Add other updatable fields here if needed
    # is_active: bool | None = None
    # subscription_tier: SubscriptionTier | None = None # Should admin be able to update?

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    is_active: bool
    full_name: str | None = None
    subscription_tier: SubscriptionTier # Add tier here
    # Add other DB fields here
    # full_name: str | None = None

    class Config:
        from_attributes = True # Pydantic V2 uses this instead of orm_mode

# Properties to return to client
class User(UserInDBBase):
    pass # Inherits all from UserInDBBase

# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str 