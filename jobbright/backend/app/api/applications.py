from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from .users import get_current_user # Import dependency for current user
from ...workers.tasks import trigger_auto_apply # Import the Celery task
from ...models.application import ApplicationStatus # Import status enum

router = APIRouter()

@router.post("/", response_model=schemas.Application, status_code=status.HTTP_201_CREATED)
def create_application(
    *, 
    db: Session = Depends(get_db), 
    application_in: schemas.ApplicationCreate, 
    current_user: models.User = Depends(get_current_user)
):
    """Create a new application record for the current user.
    
    Typically used when a user saves a job to track.
    Checks if an application for this user and job already exists.
    """
    # Check if job exists (optional, depends on desired strictness)
    job = crud.job.get_job(db, job_id=application_in.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Job with ID {application_in.job_id} not found."
        )
        
    # Check if resume exists if provided (optional)
    if application_in.resume_id:
        resume = crud.resume.get_resume(db, resume_id=application_in.resume_id)
        # Important: Check if the resume actually belongs to the current user
        if not resume or resume.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Resume with ID {application_in.resume_id} not found or does not belong to the user."
            )

    # Check if application already exists for this user/job
    existing_application = crud.application.get_application_by_user_and_job(
        db, user_id=current_user.id, job_id=application_in.job_id
    )
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application for this job already exists for the user."
        )
        
    try:
        application = crud.application.create_application(
            db=db, application_in=application_in, user_id=current_user.id
        )
        return application
    except ValueError as e: # Catch specific error from CRUD if needed
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[schemas.Application])
def read_applications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve applications for the current user."""
    applications = crud.application.get_applications_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return applications

@router.get("/{application_id}", response_model=schemas.Application)
def read_application(
    *, 
    db: Session = Depends(get_db), 
    application_id: int, 
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific application by ID, ensuring it belongs to the current user."""
    db_application = crud.application.get_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if db_application.user_id != current_user.id:
        # Although the query might be filtered, double check ownership for security
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this application")
    return db_application

@router.put("/{application_id}", response_model=schemas.Application)
def update_application(
    *, 
    db: Session = Depends(get_db), 
    application_id: int, 
    application_in: schemas.ApplicationUpdate, 
    current_user: models.User = Depends(get_current_user)
):
    """Update an application (e.g., status, notes), ensuring it belongs to the current user."""
    db_application = crud.application.get_application(db, application_id=application_id)
    if db_application is None:
    """Update a job application. Triggers auto-apply task if status changes to APPLYING and quota allows."""
    db_application = crud.application.get_application(
        db=db, application_id=application_id, user_id=current_user.id
    )
    if not db_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # --- Check if triggering auto-apply --- 
    should_trigger_apply = False
    if application_in.status == ApplicationStatus.APPLYING and db_application.status != ApplicationStatus.APPLYING:
        # Check quota before allowing the status change and triggering the task
        can_apply = crud.application.check_auto_apply_quota(db=db, user=current_user)
        if not can_apply:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                detail=f"Auto-apply quota reached for the month ({crud.application.FREE_TIER_AUTO_APPLY_LIMIT} limit for free tier)."
            )
        else:
            should_trigger_apply = True

    # Optional: Validate resume ownership if resume_id is being updated
    if application_in.resume_id and application_in.resume_id != db_application.resume_id:
        resume = crud.resume.get_resume(db=db, resume_id=application_in.resume_id)
        if not resume or resume.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume not found or does not belong to user")

    # Update the application record in the database
    updated_application = crud.application.update_application(
        db=db, db_application=db_application, application_in=application_in
    )

    # --- Trigger Celery task AFTER successfully updating status --- 
    if should_trigger_apply:
        trigger_auto_apply.delay(application_id=updated_application.id)

    return updated_application

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a tracked job application."""
    deleted_application = crud.application.delete_application(
        db=db, application_id=application_id, user_id=current_user.id
    )
    if not deleted_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    # No content is returned on successful deletion
    return None 