from sqlalchemy.orm import Session
from typing import List, Union, Optional
import logging

# Import schemas directly
from ..schemas.resume import ResumeCreate, ResumeUpdate
from ..models.resume import Resume # Import Resume model directly
from ..services import matching # Import matching service

logger = logging.getLogger(__name__)

def get_resume(db: Session, resume_id: int, owner_id: int) -> Optional[Resume]: # Use direct model import
    """
    Gets a specific resume by its ID and owner ID.
    """
    return db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == owner_id).first() # Use direct model import

def get_resumes_by_owner(
    db: Session, owner_id: int, skip: int = 0, limit: int = 100
) -> List[Resume]: # Use direct model import
    """
    Gets all resumes belonging to a specific owner.
    """
    return db.query(Resume).filter(Resume.owner_id == owner_id).offset(skip).limit(limit).all() # Use direct model import

def create_resume(
    db: Session,
    resume_in: ResumeCreate, # Use direct schema import
    owner_id: int,
    original_filepath: Optional[str] = None # Add optional parameter for S3 key
) -> Resume: # Use direct model import
    """
    Creates a new resume for a specific owner.
    """
    # Convert structured_data Pydantic model to dict for JSONB storage if present
    resume_data = resume_in.model_dump()
    if resume_data.get("structured_data"):
         # Ensure nested Pydantic models are also dumped if they exist
         if resume_in.structured_data and hasattr(resume_in.structured_data, 'model_dump'):
             resume_data["structured_data"] = resume_in.structured_data.model_dump()
         # else: # Keep raw dict if somehow it's already a dict
         #    resume_data["structured_data"] = resume_in.structured_data

    # NOTE: Embedding generation logic should be added here or in a service layer later
    db_resume = Resume( # Use direct model import
        **resume_data,
        owner_id=owner_id,
        original_filepath=original_filepath # Set the filepath from the parameter
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def update_resume(
    db: Session, db_resume: Resume, resume_in: ResumeUpdate # Use direct schema import
) -> Resume: # Use direct model import
    """
    Updates an existing resume.
    """
    update_data = resume_in.model_dump(exclude_unset=True)

    # Convert structured_data Pydantic model to dict for JSONB storage if present in update
    if "structured_data" in update_data and update_data["structured_data"] is not None:
         update_data["structured_data"] = resume_in.structured_data.model_dump() # Use .model_dump() on the nested model

    # NOTE: Embedding regeneration logic should be added here or in a service layer later if content changes
    for field, value in update_data.items():
        setattr(db_resume, field, value)
    
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def remove_resume(db: Session, resume_id: int, owner_id: int) -> Optional[Resume]: # Use direct model import
    """
    Deletes a resume by its ID and owner ID.
    Returns the deleted resume or None if not found.
    """
    db_resume = get_resume(db=db, resume_id=resume_id, owner_id=owner_id)
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume 