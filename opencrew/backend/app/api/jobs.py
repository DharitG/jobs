from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas # Import crud and schemas
from app.models.user import User # Import User model specifically
from app.db.session import get_db # Absolute import
from app.api.users import get_current_user # Absolute import

router = APIRouter()

@router.post("/", response_model=schemas.Job)
def create_job(
    *, 
    db: Session = Depends(get_db), 
    job_in: schemas.JobCreate, 
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Create a new job listing.
    
    Requires authentication. (Potentially admin only later)
    """
    # Check if job URL already exists?
    existing_job = crud.job.get_job_by_url(db, url=str(job_in.url))
    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with URL {job_in.url} already exists."
        )
    job = crud.job.create_job(db=db, job=job_in)
    return job

@router.get("/", response_model=List[schemas.Job])
def read_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Retrieve a list of job listings with pagination.
    
    Requires authentication currently.
    """
    jobs = crud.job.get_jobs(db, skip=skip, limit=limit)
    return jobs

@router.get("/{job_id}", response_model=schemas.Job)
def read_job(
    *, 
    db: Session = Depends(get_db), 
    job_id: int, 
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Get a specific job listing by ID.
    
    Requires authentication.
    """
    db_job = crud.job.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return db_job

@router.put("/{job_id}", response_model=schemas.Job)
def update_job(
    *, 
    db: Session = Depends(get_db), 
    job_id: int, 
    job_in: schemas.JobUpdate, 
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Update a job listing.
    
    Requires authentication. (Potentially admin/owner only later)
    """
    db_job = crud.job.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    # Add authorization check here later if needed (e.g., is user admin?)
    job = crud.job.update_job(db=db, db_job=db_job, job_in=job_in)
    return job

@router.delete("/{job_id}", response_model=schemas.Job)
def delete_job(
    *, 
    db: Session = Depends(get_db), 
    job_id: int, 
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Delete a job listing.
    
    Requires authentication. (Potentially admin only later)
    """
    db_job = crud.job.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    # Add authorization check here later if needed
    deleted_job = crud.job.delete_job(db=db, job_id=job_id)
    return deleted_job 