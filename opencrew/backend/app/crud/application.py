from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, extract

from .. import models, schemas
from ..models.application import ApplicationStatus # Ensure status enum is available
from ..models.user import SubscriptionTier # Import user tier enum

# Define free tier limit
FREE_TIER_AUTO_APPLY_LIMIT = 50

def get_application(db: Session, application_id: int) -> Optional[models.Application]:
    """Get a single application by ID."""
    return db.query(models.Application).filter(models.Application.id == application_id).first()

def get_applications_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Application]:
    """Get all applications for a specific user."""
    return (
        db.query(models.Application)
        .filter(models.Application.user_id == user_id)
        .order_by(models.Application.status_last_updated_at.desc()) # Example ordering
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_application_by_user_and_job(
    db: Session, user_id: int, job_id: int
) -> Optional[models.Application]:
    """Get a specific application for a user and job (to prevent duplicates)."""
    return (
        db.query(models.Application)
        .filter(models.Application.user_id == user_id, models.Application.job_id == job_id)
        .first()
    )

def count_monthly_auto_applies(db: Session, user_id: int) -> int:
    """Counts applications marked as 'applied' or 'applying' by the user in the current calendar month."""
    now = datetime.utcnow()
    # Count applications from the start of the current month
    start_of_month = datetime(now.year, now.month, 1)
    
    count = db.query(func.count(models.Application.id)).filter(
        models.Application.user_id == user_id,
        models.Application.status.in_([ApplicationStatus.APPLIED, ApplicationStatus.APPLYING]),
        # Check based on when the status was last updated or applied_at
        # Using status_last_updated_at might be simpler if 'applying' is brief
        models.Application.status_last_updated_at >= start_of_month 
        # Alternatively, check applied_at if only counting fully applied:
        # models.Application.applied_at >= start_of_month
    ).scalar()
    
    return count or 0 # Return 0 if count is None

def check_auto_apply_quota(db: Session, user: models.User) -> bool:
    """Checks if the user is allowed to perform another auto-apply based on their tier and usage.
    
    Returns:
        True if the user is within their quota, False otherwise.
    """
    # Pro and Elite tiers have unlimited applies (for now)
    if user.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ELITE]:
        return True
        
    # Check free tier quota
    if user.subscription_tier == SubscriptionTier.FREE:
        current_usage = count_monthly_auto_applies(db=db, user_id=user.id)
        if current_usage < FREE_TIER_AUTO_APPLY_LIMIT:
            return True
        else:
            return False
            
    # Default case (shouldn't happen if tier is set correctly)
    return False 

def create_application(
    db: Session, *, application_in: schemas.ApplicationCreate, user_id: int
) -> models.Application:
    """Create a new application record (e.g., when a user saves a job)."""
    # Check if application already exists for this user/job
    existing_application = get_application_by_user_and_job(db, user_id=user_id, job_id=application_in.job_id)
    if existing_application:
        # Optionally update status or return existing? For now, raise error.
        raise ValueError(f"Application for user {user_id} and job {application_in.job_id} already exists.")

    db_application = models.Application(
        **application_in.model_dump(), 
        user_id=user_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_application(
    db: Session, *, db_application: models.Application, application_in: schemas.ApplicationUpdate
) -> models.Application:
    """Update an existing application (e.g., change status, add notes)."""
    update_data = application_in.model_dump(exclude_unset=True)
    
    # Update status timestamp if status changes
    if "status" in update_data and update_data["status"] != db_application.status:
        update_data["status_last_updated_at"] = datetime.utcnow() 
        # If status is set to APPLIED, set applied_at if not already set
        if update_data["status"] == ApplicationStatus.APPLIED and db_application.applied_at is None:
            update_data["applied_at"] = datetime.utcnow()
            
    for field, value in update_data.items():
        setattr(db_application, field, value)
        
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_application_status(
    db: Session, application_id: int, status: models.ApplicationStatus
) -> Optional[models.Application]:
    """Helper function to specifically update only the status."""
    db_app = get_application(db, application_id)
    if not db_app:
        return None
    update_schema = schemas.ApplicationUpdate(status=status)
    return update_application(db=db, db_application=db_app, application_in=update_schema)

def delete_application(db: Session, *, application_id: int) -> Optional[models.Application]:
    """Delete an application record."""
    db_application = get_application(db, application_id=application_id)
    if db_application:
        db.delete(db_application)
        db.commit()
    return db_application 