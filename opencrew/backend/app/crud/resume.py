from sqlalchemy.orm import Session
from typing import List, Union, Optional
import logging

from .. import models, schemas
from ..services import matching # Import matching service

logger = logging.getLogger(__name__)

def get_resume(db: Session, resume_id: int, owner_id: int) -> Optional[models.Resume]:
    """
    Gets a specific resume by its ID and owner ID.
    """
    return db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.owner_id == owner_id).first()

def get_resumes_by_owner(
    db: Session, owner_id: int, skip: int = 0, limit: int = 100
) -> List[models.Resume]:
    """
    Gets all resumes belonging to a specific owner.
    """
    return db.query(models.Resume).filter(models.Resume.owner_id == owner_id).offset(skip).limit(limit).all()

def create_resume(
    db: Session, resume: schemas.ResumeCreate, owner_id: int
) -> models.Resume:
    """
    Creates a new resume for a specific owner.
    """
    # Convert structured_data Pydantic model to dict for JSONB storage if present
    resume_data = resume.model_dump()
    if resume_data.get("structured_data"):
         resume_data["structured_data"] = resume.structured_data.model_dump() # Use .model_dump() on the nested model

    # NOTE: Embedding generation logic should be added here or in a service layer later
    db_resume = models.Resume(**resume_data, owner_id=owner_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def update_resume(
    db: Session, db_resume: models.Resume, resume_in: schemas.ResumeUpdate
) -> models.Resume:
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

def remove_resume(db: Session, resume_id: int, owner_id: int) -> Optional[models.Resume]:
    """
    Deletes a resume by its ID and owner ID.
    Returns the deleted resume or None if not found.
    """
    db_resume = get_resume(db=db, resume_id=resume_id, owner_id=owner_id)
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume 