from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from .users import get_current_user # Dependency to get the logged-in user
from ..services import profile_import # Import the parsing service

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