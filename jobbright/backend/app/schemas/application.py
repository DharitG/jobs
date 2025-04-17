from pydantic import BaseModel
from datetime import datetime

from ..models.application import ApplicationStatus # Import the enum

# Shared properties (usually what you get when creating/updating)
class ApplicationBase(BaseModel):
    job_id: int
    resume_id: int | None = None # Optional resume used for the application
    status: ApplicationStatus = ApplicationStatus.SAVED
    notes: str | None = None

# Properties to receive on creation (might be just Job ID initially)
class ApplicationCreate(BaseModel):
    job_id: int
    # Status could be set automatically or passed in
    status: ApplicationStatus = ApplicationStatus.SAVED 
    resume_id: int | None = None # Can specify resume later

# Properties to receive on update (e.g., changing status, adding notes)
class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    resume_id: int | None = None
    notes: str | None = None
    applied_at: datetime | None = None # Allow setting applied_at timestamp

# Properties shared by models stored in DB
class ApplicationInDBBase(ApplicationBase):
    id: int
    user_id: int
    status_last_updated_at: datetime
    applied_at: datetime | None = None
    job_id: int # Ensure required fields from model are here
    status: ApplicationStatus # Ensure required fields from model are here

    class Config:
        from_attributes = True # Pydantic V2

# Properties to return to client (potentially with nested Job info)
class Application(ApplicationInDBBase):
    # If you want to include job details when returning an application:
    # from .job import Job # Import Job schema
    # job: Job | None = None
    pass

# Properties stored in DB
class ApplicationInDB(ApplicationInDBBase):
    pass 