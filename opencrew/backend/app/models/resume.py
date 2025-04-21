from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB # Changed JSON to JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base # Import Base from user model or a central base file

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(JSONB, nullable=True) # Store embedding as JSONB
    
    # File paths related to optimization process
    original_filepath = Column(String, nullable=True)
    converted_filepath = Column(String, nullable=True) # e.g., path to plain text version
    modified_filepath = Column(String, nullable=True) # e.g., path to docx with patches applied
    exported_filepath = Column(String, nullable=True) # e.g., path to final exported pdf/docx
    
    # Store optimization suggestions/diffs
    optimization_diffs = Column(JSONB, nullable=True) # Consider changing existing JSON to JSONB too for consistency? For now, just adding new one.

    # Stores the parsed and potentially tailored structured data from resume_tailoring_service
    structured_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="resumes")