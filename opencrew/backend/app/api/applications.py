from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
import os # For path validation
from pathlib import Path # For path validation
from sqlalchemy.orm import Session
from typing import List
import logging
import tempfile

from app import crud, schemas # Import crud and schemas
from app.models.user import User # Import User model specifically
from app.db.session import get_db # Absolute import
from app.api.users import get_current_user # Absolute import
from app.workers.tasks import trigger_auto_apply # Absolute import
from app.models.application import ApplicationStatus # Absolute import


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=schemas.Application, status_code=status.HTTP_201_CREATED)
def create_application(
    *, 
    db: Session = Depends(get_db), 
    application_in: schemas.ApplicationCreate, 
    current_user: User = Depends(get_current_user) # Use imported User type
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
    current_user: User = Depends(get_current_user) # Use imported User type
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
    current_user: User = Depends(get_current_user) # Use imported User type
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
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Update a job application. Triggers auto-apply task if status changes to APPLYING and quota allows."""
    # Fetch the application ensuring it belongs to the current user
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
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Delete a tracked job application."""
    deleted_application = crud.application.delete_application(
        db=db, application_id=application_id, user_id=current_user.id
    )
    if not deleted_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    # No content is returned on successful deletion
    return None 


@router.get("/{application_id}/screenshot")
async def get_application_screenshot(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Get the final screenshot associated with a specific application."""
    db_application = crud.application.get_application(db, application_id=application_id)

    if db_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if db_application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this application")
    if not db_application.screenshot_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screenshot not found for this application")

    screenshot_path = Path(db_application.screenshot_url)

    # Basic security check: Ensure the file exists and is within the expected artifact directory
    # This prevents accessing arbitrary files if the screenshot_url was somehow manipulated.
    # We rely on the fact that save_screenshot_from_history saves to a known temp dir structure.
    expected_artifact_dir = Path(tempfile.gettempdir()) / "opencrew_artifacts"
    try:
        # Ensure the path is absolute and resolves correctly
        abs_path = screenshot_path.resolve(strict=True)
        # Ensure the resolved path is within the allowed directory
        if not abs_path.is_file() or not abs_path.is_relative_to(expected_artifact_dir.resolve(strict=True)):
             raise FileNotFoundError # Treat as not found if outside allowed dir or not a file
             
    except (FileNotFoundError, Exception) as e:
        logger.error(f"Screenshot file not found or invalid path for app {application_id}: {screenshot_path}, Error: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screenshot file not found or path is invalid")

    return FileResponse(str(abs_path), media_type="image/png")
