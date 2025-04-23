import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Assume schemas are importable relative to the tests directory
from app.schemas.resume import StructuredResume, BasicInfo, ExperienceItem, EducationItem, SkillItem, ProjectItem
from app.services.pdf_generator import StructuredResumePdfGenerator

# --- Test Data ---

def create_test_resume_data() -> StructuredResume:
    """Helper function to create consistent test data."""
    return StructuredResume(
        basic=BasicInfo(
            name="Test User PDF",
            email="test.pdf@email.com",
            phone="555-123-4567",
            location="Testville, TS",
            linkedin_url="https://linkedin.com/in/testuserpdf",
            github_url="https://github.com/testuserpdf"
        ),
        objective="A test objective for PDF generation.",
        experiences=[
            ExperienceItem(company="PDF Test Corp", position="Generator", startDate="2022-01", endDate="Present", highlights=["Generated test PDFs.", "Used ReportLab."])
        ],
        projects=[
            ProjectItem(name="PDF Gen Test Project", startDate="2023", description="Testing PDF generation.")
        ],
        education=[
            EducationItem(institution="Testing University", area="PDF Studies", studyType="Bachelor of Testing", startDate="2018", endDate="2022", score="4.0")
        ],
        skills=[
            SkillItem(category="Testing Tools", skills=["pytest", "reportlab"]),
            SkillItem(category="Languages", skills=["Python"])
        ]
    )

# --- Test Cases ---

# Mocking font registration to avoid filesystem dependencies in basic tests
@patch('app.services.pdf_generator.pdfmetrics.registerFont')
@patch('app.services.pdf_generator.ttfonts.TTFont')
def test_generate_resume_pdf_basic(mock_ttfont, mock_registerfont):
    """Test basic PDF generation creates a file."""
    generator = StructuredResumePdfGenerator()
    resume_data = create_test_resume_data()
    
    # Use a temporary directory for the output PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            output_path_str = generator.generate_resume_pdf(resume_data, temp_dir)
            output_path = Path(output_path_str)

            # 1. Check if the returned path is not None and ends with .pdf
            assert output_path_str is not None
            assert output_path.suffix == ".pdf"

            # 2. Check if the file exists
            assert output_path.exists()

            # 3. Check if the filename contains the expected name part
            expected_name_part = resume_data.basic.name.replace(' ', '_')
            assert expected_name_part in output_path.stem

            # 4. Check if the file is not empty (basic check)
            assert output_path.stat().st_size > 100 # Check if file size is greater than 100 bytes

        finally:
            # Clean up the generated file if it exists (usually handled by TemporaryDirectory)
             if 'output_path' in locals() and output_path.exists():
                 try:
                     output_path.unlink()
                 except OSError:
                     # Handle potential errors during cleanup if needed
                     pass

@patch('app.services.pdf_generator.pdfmetrics.registerFont')
@patch('app.services.pdf_generator.ttfonts.TTFont')
def test_generate_resume_pdf_missing_optional_data(mock_ttfont, mock_registerfont):
    """Test PDF generation with missing optional sections."""
    generator = StructuredResumePdfGenerator()
    # Create data with only basic info and one experience
    resume_data = StructuredResume(
        basic=BasicInfo(name="Minimal User", email="min@test.com"),
        experiences=[ExperienceItem(company="MinCorp", position="Tester", highlights=["Tested minimal case."])]
        # objective, projects, education, skills are None
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            output_path_str = generator.generate_resume_pdf(resume_data, temp_dir)
            output_path = Path(output_path_str)

            # Assert file is created and seems valid
            assert output_path_str is not None
            assert output_path.suffix == ".pdf"
            assert output_path.exists()
            assert output_path.stat().st_size > 100

        finally:
             if 'output_path' in locals() and output_path.exists():
                  try:
                      output_path.unlink()
                  except OSError:
                      pass

# TODO: Add more tests:
# - Test with very long text to check wrapping.
# - Test specific formatting elements (bolding, italics, links) if possible without visual inspection.
# - Test error handling (e.g., if resume_data.basic is missing - currently raises ValueError).
# - Test font loading if STYLES_AVAILABLE is False (fallback styles).