import pytest
from app.schemas.resume import BasicInfo, SkillItem, StructuredResume
from app.services.resume_tailoring import extract_structured_data, _extract_skills, _extract_name, _find_first_match
from app.services.resume_tailoring import EMAIL_REGEX, PHONE_REGEX, LINKEDIN_REGEX # Import necessary regex

# Basic test data simulating processed lines for different sections
mock_contact_lines_basic = [
    {"text": "John Doe", "y": 100, "x": 50, "height": 12, "fontName": "Arial-Bold"},
    {"text": "San Francisco, CA", "y": 115, "x": 50, "height": 10, "fontName": "Arial"},
    {"text": "john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe", "y": 130, "x": 50, "height": 10, "fontName": "Arial"},
]

mock_skill_lines_simple = [
    {"text": "Languages: Python, Java, JavaScript", "y": 200, "x": 50, "height": 10, "fontName": "Arial"},
    {"text": "Frameworks: React, FastAPI, Node.js", "y": 215, "x": 50, "height": 10, "fontName": "Arial"},
    {"text": "Tools: Docker, Git, AWS", "y": 230, "x": 50, "height": 10, "fontName": "Arial"},
]

mock_skill_lines_categorized = [
    {"text": "Programming Languages:", "y": 200, "x": 50, "height": 11, "fontName": "Arial-Bold"},
    {"text": "Python, Java, C++, SQL", "y": 215, "x": 60, "height": 10, "fontName": "Arial"},
    {"text": "Web Technologies:", "y": 230, "x": 50, "height": 11, "fontName": "Arial-Bold"},
    {"text": "HTML, CSS, JavaScript, React, Node.js", "y": 245, "x": 60, "height": 10, "fontName": "Arial"},
    {"text": "Databases: PostgreSQL, MongoDB", "y": 260, "x": 60, "height": 10, "fontName": "Arial"},
]

mock_objective_lines = [
     {"text": "Seeking a challenging software engineer role.", "y": 150, "x": 50, "height": 10, "fontName": "Arial"},
]

mock_empty_sections = {
    "contact": [], "objective": [], "experience": [], "education": [], "projects": [], "skills": [], "unknown": []
}

# --- Test Helper Functions ---

def test_extract_name():
    assert _extract_name(mock_contact_lines_basic) == "John Doe"
    # Test case where name isn't the first line
    lines_name_second = [
        {"text": "john.doe@email.com", "y": 100, "x": 50, "height": 10, "fontName": "Arial"},
        {"text": "Jane Smith", "y": 115, "x": 50, "height": 12, "fontName": "Arial-Bold"},
    ]
    # Note: _extract_name sorts internally by height, so it should still find Jane Smith
    assert _extract_name(lines_name_second) == "Jane Smith"
    assert _extract_name([]) is None

def test_find_first_match():
    assert _find_first_match(mock_contact_lines_basic, EMAIL_REGEX) == "john.doe@email.com"
    assert _find_first_match(mock_contact_lines_basic, PHONE_REGEX) == "(123) 456-7890"
    assert _find_first_match(mock_contact_lines_basic, LINKEDIN_REGEX) == "linkedin.com/in/johndoe"
    assert _find_first_match([], EMAIL_REGEX) is None
    lines_no_match = [{"text": "Just some text", "y": 1, "x": 1, "height": 1, "fontName": ""}]
    assert _find_first_match(lines_no_match, EMAIL_REGEX) is None

def test_extract_skills_simple():
    skills = _extract_skills(mock_skill_lines_simple)
    assert len(skills) == 9 # 3 languages + 3 frameworks + 3 tools
    skill_names = {s.name for s in skills}
    assert "Python" in skill_names
    assert "React" in skill_names
    assert "Docker" in skill_names
    # All should be in 'General' category by default
    assert all(s.category == "General" for s in skills)

def test_extract_skills_categorized():
    skills = _extract_skills(mock_skill_lines_categorized)
    assert len(skills) == 11 # 4 langs + 5 web + 2 DBs
    categories = {s.category for s in skills}
    names = {s.name for s in skills}
    assert "Programming Languages" in categories
    assert "Web Technologies" in categories
    assert "Databases" not in categories # The line ending in ':' is the category header itself
    assert "Python" in names
    assert "React" in names
    assert "PostgreSQL" in names
    assert skills[0].category == "Programming Languages" # Check first category
    assert skills[4].category == "Web Technologies"    # Check switch

# --- Test Main Extraction Function ---

def test_extract_structured_data_basic():
    """Tests extraction of basic info, objective, and simple skills."""
    mock_sections = {
        "contact": mock_contact_lines_basic,
        "objective": mock_objective_lines,
        "experience": [],
        "education": [],
        "projects": [],
        "skills": mock_skill_lines_simple,
        "unknown": []
    }
    result = extract_structured_data(mock_sections)

    assert isinstance(result, StructuredResume)
    # Basic Info Checks
    assert result.basic is not None
    assert result.basic.name == "John Doe"
    assert result.basic.email == "john.doe@email.com"
    assert result.basic.phone == "(123) 456-7890"
    assert result.basic.linkedin_url == "linkedin.com/in/johndoe"
    # Objective Check
    assert result.objective == "Seeking a challenging software engineer role."
    # Skills Check
    assert result.skills is not None
    assert len(result.skills) == 9
    assert result.skills[0].name == "Python" # Assumes order based on simple extraction

def test_extract_structured_data_categorized_skills():
    """Tests extraction with categorized skills."""
    mock_sections = {
        "contact": [],
        "objective": [],
        "experience": [],
        "education": [],
        "projects": [],
        "skills": mock_skill_lines_categorized,
        "unknown": []
    }
    result = extract_structured_data(mock_sections)
    assert result.skills is not None
    assert len(result.skills) == 11
    assert any(s.name == "Java" and s.category == "Programming Languages" for s in result.skills)
    assert any(s.name == "Node.js" and s.category == "Web Technologies" for s in result.skills)
    assert any(s.name == "MongoDB" and s.category == "Web Technologies" for s in result.skills) # Should inherit last category

def test_extract_structured_data_empty():
    """Tests extraction with empty sections."""
    result = extract_structured_data(mock_empty_sections)
    assert isinstance(result, StructuredResume)
    assert result.basic is not None # BasicInfo should always be created
    assert result.basic.name is None
    assert result.objective is None
    assert result.skills == []
    assert result.education == []
    assert result.experiences == []

# TODO: Add tests for _extract_education and _extract_experience once they have more robust logic