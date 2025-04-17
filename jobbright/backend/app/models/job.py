import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON
# Consider using sqlalchemy_utils.types.url.URLType for url if installed
# from sqlalchemy.dialects.postgresql import VECTOR # Example if using pgvector

from .user import Base # Assuming Base is defined centrally or in user.py
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    company = Column(String, index=True, nullable=True)
    location = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String, unique=True, index=True, nullable=False) # Job URLs should be unique
    source = Column(String, index=True, nullable=True) # e.g., 'Indeed', 'LinkedIn', 'Greenhouse'
    date_posted = Column(DateTime, nullable=True)
    visa_sponsorship_available = Column(Boolean, default=False, nullable=True)
    
    # Placeholder for vector embedding - type depends on DB (e.g., pgvector)
    # embedding = Column(VECTOR(768)) # Example dimension 768
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship to Applications (One Job can have many Applications)
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    
    # Add relationships if jobs are linked to users (e.g., saved jobs, applications)
    # Example: user_applications = relationship("User", secondary="job_applications", back_populates="applied_jobs") 