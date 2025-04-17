import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    full_name = Column(String, index=True, nullable=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    
    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    
    # Add other fields as needed, e.g., subscription_status, etc.
    # subscription_tier = Column(String, default="free") 