import pytest
import json
from unittest.mock import patch, MagicMock
from app.schemas.resume import BasicInfo, SkillItem, StructuredResume, PdfTextItem, ExperienceItem
from app.services.resume_tailoring import process_and_tailor_resume

# --- Test Data ---

# Mock PdfTextItem list representing some raw text
mock_text_items = [
    PdfTextItem(text="John Doe\n", fontName="Arial", width=100, height=12, x=10, y=10, hasEOL=True),
    PdfTextItem(text="Software Engineer\n", fontName="Arial", width=100, height=10, x=10, y=25, hasEOL=True),
    PdfTextItem(text="john.doe@email.com | 123-456-7890\n", fontName="Arial", width=200, height=10, x=10, y=40, hasEOL=True),
    PdfTextItem(text="Experience\n", fontName="Arial-Bold", width=100, height=11, x=10, y=60, hasEOL=True),
    PdfTextItem(text="Tech Corp - Software Engineer (2020-Present)\n", fontName="Arial", width=200, height=10, x=10, y=75, hasEOL=True),
    PdfTextItem(text="- Developed feature X\n", fontName="Arial", width=150, height=10, x=20, y=90, hasEOL=True),
    PdfTextItem(text="Skills\n", fontName="Arial-Bold", width=100, height=11, x=10, y=110, hasEOL=True),
    PdfTextItem(text="Python, FastAPI, Docker\n", fontName="Arial", width=150, height=10, x=10, y=125, hasEOL=True),
]

# Mock successful LLM response for parsing
mock_llm_parse_success_json = json.dumps({
    "basic": {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "123-456-7890",
        "location": None, "linkedin_url": None, "github_url": None, "portfolio_url": None
    },
    "objective": "Software Engineer",
    "education": [],
    "experiences": [{
        "company": "Tech Corp",
        "position": "Software Engineer",
        "website": None, "startDate": "2020", "endDate": "Present",
        "summary": None, "highlights": ["Developed feature X"]
    }],
    "projects": [],
    "skills": [
        {"category": "Programming Languages", "skills": ["Python"]},
        {"category": "Frameworks", "skills": ["FastAPI"]},
        {"category": "Tools", "skills": ["Docker"]}
    ]
})

# Mock successful LLM response for tailoring the objective
mock_llm_tailor_objective_response = "Highly motivated Software Engineer seeking opportunity at TargetCorp."

# Mock successful LLM response for tailoring skills
mock_llm_tailor_skills_response = "Python, Docker" # Assume job only mentioned these

# Mock successful LLM response for tailoring experience
mock_llm_tailor_experience_response = "- Led development of feature X relevant to TargetCorp requirements."

# Mock job description
mock_job_description = "Seeking a Python developer with Docker experience at TargetCorp."


# --- Test Cases ---

@patch('app.services.resume_tailoring._call_llm')
def test_process_and_tailor_success_parsing_only(mock_call_llm: MagicMock):
    """Test successful parsing when no job description is provided."""
    # Mock LLM response for the parsing call
    mock_call_llm.return_value = mock_llm_parse_success_json

    result = process_and_tailor_resume(text_items=mock_text_items, job_description=None)

    # Assertions
    assert isinstance(result, StructuredResume)
    assert mock_call_llm.call_count == 1 # Only parsing call should happen
    assert result.basic.name == "John Doe"
    assert result.objective == "Software Engineer" # Original objective from parsing
    assert len(result.experiences) == 1
    assert result.experiences[0].company == "Tech Corp"
    assert result.experiences[0].highlights == ["Developed feature X"] # Original highlights
    assert len(result.skills) == 3

@patch('app.services.resume_tailoring._call_llm')
def test_process_and_tailor_success_with_tailoring(mock_call_llm: MagicMock):
    """Test successful parsing and tailoring when job description is provided."""
    # Mock LLM responses: First for parsing, then for each tailoring step
    mock_call_llm.side_effect = [
        mock_llm_parse_success_json,          # 1. Parsing result
        mock_llm_tailor_objective_response,   # 2. Tailor objective
        mock_llm_tailor_skills_response,      # 3. Tailor skills
        mock_llm_tailor_experience_response   # 4. Tailor experience 1
    ]

    result = process_and_tailor_resume(text_items=mock_text_items, job_description=mock_job_description)

    # Assertions
    assert isinstance(result, StructuredResume)
    assert mock_call_llm.call_count == 4 # Parsing + objective + skills + 1 experience
    assert result.basic.name == "John Doe"
    # Check tailored content
    assert result.objective == mock_llm_tailor_objective_response
    assert len(result.skills) == 1 # Only one category returned
    assert result.skills[0].category == "Relevant Skills"
    assert set(result.skills[0].skills) == {"Python", "Docker"}
    assert len(result.experiences) == 1
    assert result.experiences[0].highlights == [mock_llm_tailor_experience_response] # Should be list of strings

@patch('app.services.resume_tailoring._call_llm')
def test_process_and_tailor_llm_parsing_error(mock_call_llm: MagicMock):
    """Test handling when the LLM parsing call fails (returns None)."""
    mock_call_llm.return_value = None # Simulate LLM failure during parsing

    result = process_and_tailor_resume(text_items=mock_text_items, job_description=mock_job_description)

    assert isinstance(result, StructuredResume)
    assert mock_call_llm.call_count == 1 # Only parsing call attempted
    assert result.objective == "Failed to parse resume content via LLM."
    assert result.basic is not None # Basic should exist but be empty
    assert result.experiences is None # Other fields should be None or empty

@patch('app.services.resume_tailoring._call_llm')
def test_process_and_tailor_llm_json_decode_error(mock_call_llm: MagicMock):
    """Test handling when the LLM returns invalid JSON."""
    mock_call_llm.return_value = "This is not JSON" # Simulate invalid JSON

    result = process_and_tailor_resume(text_items=mock_text_items, job_description=mock_job_description)

    assert isinstance(result, StructuredResume)
    assert mock_call_llm.call_count == 1
    assert result.objective == "Failed to parse LLM JSON response."
    assert result.basic is not None

@patch('app.services.resume_tailoring._call_llm')
def test_process_and_tailor_llm_validation_error(mock_call_llm: MagicMock):
    """Test handling when the LLM returns JSON that fails Pydantic validation."""
    # Simulate JSON missing a required field (e.g., 'company' in experiences)
    invalid_structure_json = json.dumps({
        "basic": {"name": "John Doe"},
        "experiences": [{"position": "Engineer"}] # Missing 'company'
    })
    mock_call_llm.return_value = invalid_structure_json

    result = process_and_tailor_resume(text_items=mock_text_items, job_description=mock_job_description)

    assert isinstance(result, StructuredResume)
    assert mock_call_llm.call_count == 1
    assert result.objective == "LLM response failed validation."
    assert result.basic is not None

def test_process_and_tailor_empty_input():
    """Test handling when the input text_items list is empty."""
    result = process_and_tailor_resume(text_items=[], job_description=mock_job_description)

    assert isinstance(result, StructuredResume)
    assert result.objective == "No text content found in resume."
    assert result.basic is not None

# Note: Tailoring failures (LLM returning None during tailoring) are handled internally
# by keeping the original parsed data for that specific field, so we don't need
# explicit separate tests for each tailoring step failing, unless we want to verify
# that specific behaviour (e.g., objective stays original if tailoring fails).
# The test_process_and_tailor_success_with_tailoring already covers the success path.