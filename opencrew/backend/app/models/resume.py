from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.types import JSON # Use generic JSON for broader compatibility (SQLite)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base # Import Base from user model or a central base file

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True) # Use generic JSON
    
    # File paths related to optimization process
    original_filepath = Column(String, nullable=True)
    converted_filepath = Column(String, nullable=True) # e.g., path to plain text version
    modified_filepath = Column(String, nullable=True) # e.g., path to docx with patches applied
    exported_filepath = Column(String, nullable=True) # e.g., path to final exported pdf/docx
    
    # Store optimization suggestions/diffs
    optimization_diffs = Column(JSON, nullable=True) # Use generic JSON

    # Stores the parsed and potentially tailored structured data from resume_tailoring_service
    structured_data = Column(JSON, nullable=True) # Use generic JSON

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="resumes")