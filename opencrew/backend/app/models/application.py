import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base # Assuming Base is defined centrally or in user.py

# Define potential application statuses using Python Enum
class ApplicationStatus(str, enum.Enum):
    SAVED = "saved" # User saved the job, hasn't applied
    APPLYING = "applying" # Auto-apply in progress
    APPLIED = "applied" # Application submitted
    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True) # Optional: Link the specific resume used
    
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.SAVED, index=True)
    status_last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    applied_at = Column(DateTime(timezone=True), nullable=True) # Timestamp when application was actually sent
    notes = Column(Text, nullable=True)

    # Relationships (adjust back_populates as needed)
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume") # One-way reference to resume used, or add back_populates if needed 