from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional # For embedding if used

# Shared properties
class JobBase(BaseModel):
    title: str
    url: HttpUrl # Use HttpUrl for URL validation
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    date_posted: Optional[datetime] = None
    visa_sponsorship_available: Optional[bool] = None
    # embedding: Optional[List[float]] = None # Example if embedding is returned

# Properties to receive via API on creation
class JobCreate(JobBase):
    # url is required on creation
    pass 

# Properties to receive via API on update
class JobUpdate(JobBase):
    # Allow updating any base field, make them all optional
    title: Optional[str] = None
    url: Optional[HttpUrl] = None 
    # company, location, description, etc. are already optional in JobBase
    
# Properties shared by models stored in DB
class JobInDBBase(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # embedding: Optional[List[float]] = None # If you store embedding in DB

    class Config:
        from_attributes = True # Pydantic V2

# Properties to return to client (API response)
class Job(JobInDBBase):
    pass

# Properties stored in DB
class JobInDB(JobInDBBase):
    # Add fields here that are in DB but not usually returned to users
    # (Currently none specific to Job beyond JobInDBBase)
    pass 