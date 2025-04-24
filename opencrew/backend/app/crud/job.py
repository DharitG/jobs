from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..schemas.job import JobCreate, JobUpdate # Import specific schemas
from ..models.job import Job # Import the specific Job model class
from ..services import matching # Import the matching service

logger = logging.getLogger(__name__)

def get_job(db: Session, job_id: int) -> Optional[Job]:
    """Get a single job by ID."""
    return db.query(Job).filter(Job.id == job_id).first()

def get_job_by_url(db: Session, url: str) -> Optional[Job]:
    """Get a single job by its unique URL."""
    return db.query(Job).filter(Job.url == url).first()

def get_jobs(
    db: Session, skip: int = 0, limit: int = 100, 
    # Add filters as needed, e.g., company: Optional[str] = None
) -> List[Job]:
    """Get a list of jobs with pagination."""
    query = db.query(Job)
    # Example filter:
    # if company:
    #     query = query.filter(models.Job.company.ilike(f"%{company}%"))
    return query.offset(skip).limit(limit).all()

def create_job(db: Session, job: JobCreate) -> Job:
    """Create a new job."""
    db_job = Job(
        title=job.title,
        url=str(job.url), # Convert HttpUrl back to string for DB
        company=job.company,
        location=job.location,
        description=job.description,
        source=job.source,
        date_posted=job.date_posted,
        visa_sponsorship_available=job.visa_sponsorship_available,
        # Embedding will be generated below
    )
    
    # Generate embedding if description exists
    if db_job.description:
        embedding = matching.get_embedding(db_job.description)
        if embedding:
            db_job.embedding = embedding # Store as JSON
        else:
            logger.warning(f"Could not generate embedding for new job: {db_job.title}")
            # db_job.embedding remains None
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, db_job: Job, job_in: JobUpdate) -> Job:
    """Update an existing job."""
    update_data = job_in.model_dump(exclude_unset=True)
    
    # Generate new embedding if description is updated
    if "description" in update_data:
        if update_data["description"]:
            embedding = matching.get_embedding(update_data["description"])
            if embedding:
                update_data["embedding"] = embedding
            else:
                logger.warning(f"Could not generate embedding during update for job: {db_job.id}")
                update_data["embedding"] = None # Nullify if update fails
        else:
            # Description removed or set to None
            update_data["embedding"] = None

    for field, value in update_data.items():
        # Prevent direct update of embedding if description wasn't updated
        if field == "embedding" and "description" not in update_data:
            continue
        # Convert HttpUrl back to string if url is updated
        if field == 'url' and value is not None:
            value = str(value)
        setattr(db_job, field, value)
        
    # Manually update updated_at if not handled by DB trigger/default
    # db_job.updated_at = datetime.datetime.utcnow() 
        
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int) -> Optional[Job]:
    """Delete a job by ID."""
    db_job = get_job(db, job_id=job_id)
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job

# Add more complex queries or operations as needed
# e.g., find_jobs_by_embedding, get_jobs_by_source, etc.

# Add functions for filtering/searching jobs later, e.g.:
# def search_jobs(db: Session, query: str, ...) -> List[models.Job]:
#     ... 