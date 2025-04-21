from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import List, Dict, Any


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
    job_description: str | None = None 
    job_id: int | None = None

# --- Schemas defining the structured ATS-friendly output --- 

class BasicInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

class EducationItem(BaseModel):
    institution: str
    area: str | None = None # e.g., Computer Science
    studyType: str | None = None # e.g., Bachelor of Science
    startDate: str | None = None
    endDate: str | None = None
    score: str | None = None # e.g., GPA
    courses: List[str] | None = None
    highlights: List[str] | None = None # Tailored highlights

class ExperienceItem(BaseModel):
    company: str
    position: str
    website: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    summary: str | None = None
    highlights: List[str] | None = None # Tailored highlights

class ProjectItem(BaseModel):
    name: str
    description: str | None = None
    keywords: List[str] | None = None
    url: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    highlights: List[str] | None = None # Tailored highlights

class SkillItem(BaseModel):
    category: str # e.g., Programming Languages, Frameworks, Tools
    skills: List[str]

# Schema for the structured ATS-friendly resume output from the backend
class StructuredResume(BaseModel):
    basic: BasicInfo | None = None
    objective: str | None = None # Tailored objective/summary
    education: List[EducationItem] | None = None
    experiences: List[ExperienceItem] | None = None
    projects: List[ProjectItem] | None = None
    skills: List[SkillItem] | None = None

# Response model for the parsing/tailoring endpoint
class ResumeParseResponse(BaseModel):
    structured_resume: StructuredResume
    message: str | None = None
