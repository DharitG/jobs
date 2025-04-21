from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...schemas.resume import ResumeParseRequest, ResumeParseResponse, BasicInfo, StructuredResume # Import new schemas correctly
from ...db.session import get_db
from .users import get_current_user # Dependency to get the logged-in user
from ..services import profile_import # Import the old parsing service
from ..services import resume_tailoring # Import the new tailoring service
import logging # Import logging

logger = logging.getLogger(__name__) # Add logger

router = APIRouter()

@router.post("/upload", response_model=schemas.Resume)
async def upload_resume(
    *, 
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a resume PDF, parse it, and save it for the current user."""
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only PDF is allowed."
        )
    
    try:
        resume_text = profile_import.parse_pdf_to_text(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error parsing PDF: {e}"
        )
        
    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not extract text from PDF."
        )
        
    resume_in = schemas.ResumeCreate(filename=file.filename, content=resume_text)
    new_resume = crud.resume.create_resume(db=db, resume_in=resume_in, owner_id=current_user.id)
    return new_resume

@router.get("/", response_model=List[schemas.Resume])
def read_resumes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve resumes for the current user."""
    resumes = crud.resume.get_resumes_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return resumes

@router.get("/{resume_id}", response_model=schemas.Resume)
def read_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve a specific resume by ID."""
    db_resume = crud.resume.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if db_resume.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resume")
    return db_resume

@router.put("/{resume_id}", response_model=schemas.Resume)
def update_existing_resume(
    resume_id: int,
    resume_in: schemas.ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update a specific resume."""
    db_resume = crud.resume.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if db_resume.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this resume")
    updated_resume = crud.resume.update_resume(db=db, db_resume=db_resume, resume_in=resume_in)
    return updated_resume

@router.delete("/{resume_id}", response_model=schemas.Resume)
def delete_existing_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a specific resume."""
    db_resume = crud.resume.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if db_resume.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this resume")
    deleted_resume = crud.resume.delete_resume(db=db, resume_id=resume_id)
    # The CRUD function already returns the deleted object or None
    if deleted_resume is None: # Should not happen if checks above passed, but good practice
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found during deletion")
    return deleted_resume 


# --- Endpoint for Structured PDF Parsing and Tailoring --- 

@router.post("/parse-and-tailor", response_model=ResumeParseResponse)
async def parse_and_tailor_resume(
    *, 
    db: Session = Depends(get_db),
    parse_request: schemas.ResumeParseRequest, # Use the new input schema
    current_user: models.User = Depends(get_current_user)
):
    """
    Receives parsed PDF text items from the frontend,
    triggers backend processing/tailoring,
    and returns a structured ATS-friendly resume.
    """
    logger.info(f"Received request to parse/tailor resume for user {current_user.id}. Job ID: {parse_request.job_id}")
    logger.info(f"Received {len(parse_request.text_items)} text items.")
    
    try:
        # Call the new service function (currently uses placeholder logic)
        structured_resume = resume_tailoring.process_and_tailor_resume(
            text_items=parse_request.text_items,
            job_description=parse_request.job_description
            # TODO: Potentially fetch job description from DB using job_id if not provided directly
        )
        
        # TODO: Add logic here to save/update the structured_resume in the database
        # For example, associate it with the user or a specific resume record.
        # E.g., crud.resume.update_resume_structured_data(db, resume_id=???, structured_data=structured_resume)
        
        return schemas.ResumeParseResponse(
            structured_resume=structured_resume,
            message="Resume processed and tailored successfully (using placeholder logic)."
        )
        
    except Exception as e:
        logger.exception(f"Error during parse_and_tailor_resume for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and tailor resume: {e}"
        )
