from pydantic import BaseModel
from datetime import datetime
from typing import List

# Shared properties
class ResumeBase(BaseModel):
    filename: str | None = None
    content: str # Assuming text content for now

# Properties to receive via API on creation
class ResumeCreate(ResumeBase):
    pass # Currently same as Base, might change if file upload handled differently

# Properties to receive via API on update
class ResumeUpdate(ResumeBase):
    filename: str | None = None # Make fields optional for update
    content: str | None = None
    embedding: List[float] | None = None # Allow updating embedding

# Properties shared by models stored in DB
class ResumeInDBBase(ResumeBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime | None = None
    embedding: List[float] | None = None # Add embedding field

    class Config:
        from_attributes = True # Pydantic V2

# Properties to return to client
class Resume(ResumeInDBBase):
    pass # Inherits all from ResumeInDBBase, adjust if needed

# Properties stored in DB (potentially including relationships)
class ResumeInDB(ResumeInDBBase):
    pass 