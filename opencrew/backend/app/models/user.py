import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, Date, DateTime, func, Index
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, Date, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_sub = Column(String, unique=True, index=True, nullable=False) # Auth0 Subject ID
    email = Column(String, unique=True, index=True, nullable=False)
    # hashed_password = Column(String, nullable=False) # Removed for Auth0
    is_active = Column(Boolean, default=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    full_name = Column(String, index=True, nullable=True) # Keep for potential display/legacy use
    phone_number = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    last_streak_update = Column(DateTime, nullable=True, default=None) # Stores timestamp of last activity contributing to streak

    # Stripe specific fields
    stripe_customer_id = Column(String, unique=True, index=True, nullable=True)
    stripe_subscription_id = Column(String, unique=True, index=True, nullable=True)
    stripe_subscription_status = Column(String, index=True, nullable=True) # e.g., 'active', 'canceled', 'past_due', 'trialing'
    subscription_current_period_end = Column(DateTime, nullable=True) # Store when the current sub period ends


    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")

    # Add other fields as needed, e.g., subscription_status, etc.
