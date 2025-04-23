from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional # Add Optional import


# Shared properties
class ResumeBase(BaseModel):
    filename: Optional[str] = None
    content: str # Assuming text content for now
    # Store as JSON in DB, handled as dict/Any in Pydantic
    embedding: Optional[Any] = None
    optimization_diffs: Optional[Any] = None
    structured_data: Optional['StructuredResume'] = None # Forward reference using Optional

# Properties to receive via API on creation
class ResumeCreate(ResumeBase):
    pass # Currently same as Base, might change if file upload handled differently

# Properties to receive via API on update
class ResumeUpdate(BaseModel): # Inherit directly from BaseModel for full control
    filename: Optional[str] = None
    content: Optional[str] = None
    embedding: Optional[Any] = None # Allow updating embedding
    optimization_diffs: Optional[Any] = None
    structured_data: Optional['StructuredResume'] = None # Allow updating structured_data using Optional

# Properties shared by models stored in DB
class ResumeInDBBase(ResumeBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    embedding: Optional[Any] = None # DB stores JSONB
    optimization_diffs: Optional[Any] = None # DB stores JSONB
    structured_data: Optional[Any] = None # DB stores JSONB using Optional

    class Config:
        from_attributes = True # Pydantic V2

# Properties to return to client
class Resume(ResumeInDBBase):
    original_filepath: Optional[str] = None # Add the missing field
    pass # Inherits all from ResumeInDBBase, adjust if needed

# Properties stored in DB (potentially including relationships)
class ResumeInDB(ResumeInDBBase):
    pass 


# --- Schemas for Structured PDF Parsing and ATS Template Generation --- 

# Schema for individual text items extracted by pdfjs
class PdfTextItem(BaseModel):
    text: str
    fontName: str
    width: float
    height: float
    x: float
    y: float
    hasEOL: bool

# Schema for the input request containing the parsed PDF data
class ResumeParseRequest(BaseModel):
    text_items: List[PdfTextItem]
    # Optionally include job description or job ID here if needed for tailoring
    job_description: Optional[str] = None
    job_id: Optional[int] = None
    resume_id: Optional[int] = None # ID of the existing resume to update

# --- Schemas defining the structured ATS-friendly output ---

class BasicInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class EducationItem(BaseModel):
    institution: str
    area: Optional[str] = None # e.g., Computer Science
    studyType: Optional[str] = None # e.g., Bachelor of Science
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    score: Optional[str] = None # e.g., GPA
    courses: Optional[List[str]] = None
    highlights: Optional[List[str]] = None # Tailored highlights

class ExperienceItem(BaseModel):
    company: str
    position: str
    website: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None # Tailored highlights

class ProjectItem(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    highlights: Optional[List[str]] = None # Tailored highlights

class SkillItem(BaseModel):
    category: str # e.g., Programming Languages, Frameworks, Tools
    skills: List[str]

# Schema for the structured ATS-friendly resume output from the backend
class StructuredResume(BaseModel):
    basic: Optional[BasicInfo] = None
    objective: Optional[str] = None # Tailored objective/summary
    education: Optional[List[EducationItem]] = None
    experiences: Optional[List[ExperienceItem]] = None
    projects: Optional[List[ProjectItem]] = None
    skills: Optional[List[SkillItem]] = None

# Allow forward reference resolution
ResumeBase.model_rebuild()
ResumeUpdate.model_rebuild()


# Response model for the parsing/tailoring endpoint
class ResumeParseResponse(BaseModel):
    structured_resume: StructuredResume
    message: Optional[str] = None
