import logging
import os
from pathlib import Path
from typing import List, Optional
import tempfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    HRFlowable,
)

# Attempt to import styles from the open_source_reuse location
# This assumes the structure remains accessible relative to the backend root
try:
    from open_source_reuse.pdf_generation import resume_pdf_styles
    from open_source_reuse.resources import fonts # To locate font directory if needed
    FONT_DIR = Path(fonts.__file__).parent
    STYLES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import resume_pdf_styles or fonts from open_source_reuse: {e}. Using basic styles.")
    # Define fallback styles if import fails
    STYLES_AVAILABLE = False
    # Basic Fallback Styles (Consider defining more robust fallbacks if needed)
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    resume_pdf_styles = type('obj', (object,), {
        'PARAGRAPH_STYLES': {
            'name': styles['h1'],
            'contact': styles['Normal'],
            'section': styles['h2'],
            'objective': styles['Normal'],
            'company_heading': styles['h3'],
            'company_duration': styles['Normal'],
            'company_title': styles['h4'],
            'company_location': styles['Normal'],
            'bullet_points': styles['Normal'],
            'last_bullet_point': styles['Normal'],
            'education': styles['Normal'],
            'skills': styles['Normal'],
            'link': styles['Normal'], # Add basic link style
            'link-no-hyperlink': styles['Normal'], # Add basic link style
        },
        'FONT_NAMES': {'normal': 'Helvetica', 'bold': 'Helvetica-Bold', 'italic': 'Helvetica-Oblique'},
        'FONT_PATHS': {}, # Cannot register fonts without paths
        'DEFAULT_PADDING': (1, 1),
        'DEBUG_STYLE': ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        'DOCUMENT_ALIGNMENT': [('ALIGN', (0, 0), (-1, 0), 'CENTER'), ('ALIGN', (0, 1), (-1, 1), 'CENTER')], # Example Alignment
        'FULL_COLUMN_WIDTH': A4[0] - 2 * inch, # Example width calculation
        'generate_doc_template': lambda name, output_dir: (
             SimpleDocTemplate(os.path.join(output_dir, f"{name}_resume.pdf"), pagesize=A4, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch),
             os.path.join(output_dir, f"{name}_resume.pdf")
        )
    })() # Instantiate the dummy object
    # Set alignment for fallback styles
    resume_pdf_styles.PARAGRAPH_STYLES['name'].alignment = TA_CENTER
    resume_pdf_styles.PARAGRAPH_STYLES['contact'].alignment = TA_CENTER
    resume_pdf_styles.PARAGRAPH_STYLES['company_duration'].alignment = TA_RIGHT
    resume_pdf_styles.PARAGRAPH_STYLES['company_location'].alignment = TA_RIGHT


# Import the Pydantic schema
from ..schemas.resume import StructuredResume, BasicInfo, EducationItem, ExperienceItem, ProjectItem, SkillItem

logger = logging.getLogger(__name__)

class StructuredResumePdfGenerator:
    """
    Generates a resume PDF from a StructuredResume Pydantic object using ReportLab.
    Adapted from open_source_reuse/pdf_generation/resume_pdf_generator.py
    """

    def __init__(self):
        """Initialize the Generator by registering fonts if styles were loaded."""
        if STYLES_AVAILABLE:
            self._register_fonts()
        else:
             logger.warning("Skipping font registration as styles were not loaded.")

    def _register_fonts(self):
        """Register fonts for use in the PDF."""
        # Adjust path logic if necessary, assuming FONT_DIR is correctly set
        for style, path in resume_pdf_styles.FONT_PATHS.items():
            try:
                # Construct absolute path if FONT_DIR is valid
                font_path = path # Assume path is absolute or findable by reportlab
                if FONT_DIR and not os.path.isabs(path):
                    potential_path = FONT_DIR / path
                    if potential_path.exists():
                         font_path = str(potential_path)
                    else:
                         logger.warning(f"Font file not found at relative path: {path} from {FONT_DIR}")
                         continue # Skip registration if file not found

                logger.info(f"Registering font: {resume_pdf_styles.FONT_NAMES[style]} from {font_path}")
                pdfmetrics.registerFont(ttfonts.TTFont(resume_pdf_styles.FONT_NAMES[style], font_path))
            except Exception as e:
                logger.error(f"Failed to register font {style} from {path}: {e}")


    def _append_section_table_style(self, table_styles, row_index):
        """Append styles for section headers."""
        table_styles.extend(
            [
                ("TOPPADDING", (0, row_index), (1, row_index), 5),
                ("BOTTOMPADDING", (0, row_index), (1, row_index), 2),
                ("LINEBELOW", (0, row_index), (-1, row_index), 0.1, colors.black),
            ]
        )

    def _add_table_row(
        self,
        table_data,
        table_styles,
        row_index,
        content_style_map,
        span=False,
        padding=resume_pdf_styles.DEFAULT_PADDING,
        bullet_point=None,
    ):
        """Add a row to the table."""
        row_content = []
        for content, style in content_style_map:
            # Ensure content is a string, handle None gracefully
            text_content = str(content) if content is not None else ""
            # Ensure style object is valid
            para_style = style if style else resume_pdf_styles.PARAGRAPH_STYLES.get('Normal', ParagraphStyle(name='FallbackNormal'))
            # Create Paragraph, handling bullet points
            if bullet_point:
                 row_content.append(Paragraph(text_content, bulletText=bullet_point, style=para_style))
            else:
                 row_content.append(Paragraph(text_content, style=para_style))

        table_data.append(row_content)

        table_styles.extend(
            [
                ("BOTTOMPADDING", (0, row_index), (-1, row_index), padding[0]),
                ("TOPPADDING", (0, row_index), (-1, row_index), padding[1]),
            ]
        )
        if span:
            table_styles.append(("SPAN", (0, row_index), (1, row_index)))

        return row_index + 1

    def add_experiences(self, table_data, table_styles, row_index, experiences: Optional[List[ExperienceItem]]):
        """Add experiences section."""
        if not experiences:
            return row_index

        row_index = self._add_table_row(
            table_data=table_data, table_styles=table_styles, row_index=row_index,
            content_style_map=[("Experience", resume_pdf_styles.PARAGRAPH_STYLES.get("section"))],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for exp in experiences:
            # Format dates, handle 'Present' or None
            start_date_str = exp.startDate or "?"
            end_date_str = exp.endDate or "Present"
            duration = f"{start_date_str} - {end_date_str}"

            # Company Heading row
            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[
                    (exp.company or "N/A", resume_pdf_styles.PARAGRAPH_STYLES.get("company_heading")),
                    (duration, resume_pdf_styles.PARAGRAPH_STYLES.get("company_duration")),
                ],
            )

            # Position/Title row
            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[
                    (exp.position or "N/A", resume_pdf_styles.PARAGRAPH_STYLES.get("company_title")),
                    ("", resume_pdf_styles.PARAGRAPH_STYLES.get("company_location")), # Placeholder for location if added to schema
                ],
            )

            # Highlights (Bullet Points)
            if exp.highlights:
                for i, highlight in enumerate(exp.highlights):
                    clean_highlight = highlight.replace("'", "").replace('"', "").strip() if highlight else ""
                    style = (
                        resume_pdf_styles.PARAGRAPH_STYLES.get("last_bullet_point")
                        if i == len(exp.highlights) - 1
                        else resume_pdf_styles.PARAGRAPH_STYLES.get("bullet_points")
                    )
                    padding = (5, 1) if i == len(exp.highlights) - 1 else (0, 1)

                    row_index = self._add_table_row(
                        table_data=table_data, table_styles=table_styles, bullet_point="•", row_index=row_index,
                        content_style_map=[(clean_highlight, style)],
                        span=True, padding=padding,
                    )
            elif exp.summary: # Fallback to summary if no highlights
                 row_index = self._add_table_row(
                        table_data=table_data, table_styles=table_styles, row_index=row_index,
                        content_style_map=[(exp.summary, resume_pdf_styles.PARAGRAPH_STYLES.get("bullet_points"))],
                        span=True, padding=(5,1)
                    )


        return row_index

    def add_projects(self, table_data, table_styles, row_index, projects: Optional[List[ProjectItem]]):
        """Add projects section."""
        if not projects:
            return row_index

        row_index = self._add_table_row(
            table_data=table_data, table_styles=table_styles, row_index=row_index,
            content_style_map=[("Projects", resume_pdf_styles.PARAGRAPH_STYLES.get("section"))],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for project in projects:
            project_name = project.name or "N/A"
            # Format dates, handle 'Present' or None
            start_date_str = project.startDate or "?"
            end_date_str = project.endDate or "Ongoing"
            duration = f"{start_date_str} - {end_date_str}"

            # Project Heading row (potentially with link)
            heading_text = project_name
            heading_style = resume_pdf_styles.PARAGRAPH_STYLES.get("company_heading") # Reuse style

            if project.url:
                raw_link = project.url
                clean_link = raw_link.replace("https://", "").replace("http://", "").replace("www.", "")
                hyperlink_text = f'<a href="{raw_link}">{clean_link}</a>'
                link_style = resume_pdf_styles.PARAGRAPH_STYLES.get("link")
                link_color_hex = '#' + link_style.textColor.hexval()[2:] if STYLES_AVAILABLE and hasattr(link_style.textColor, 'hexval') else '#0000EE' # Fallback blue

                # Combine heading and link - Adjust font names/sizes based on actual styles
                heading_font_name = getattr(heading_style, 'fontName', resume_pdf_styles.FONT_NAMES.get('bold', 'Helvetica-Bold'))
                heading_font_size = getattr(heading_style, 'fontSize', 11)
                link_font_name = getattr(link_style, 'fontName', resume_pdf_styles.FONT_NAMES.get('normal', 'Helvetica'))
                link_font_size = getattr(link_style, 'fontSize', 10)

                paragraph_text = (
                     f'<font name="{heading_font_name}" size="{heading_font_size}">'
                     f'{project_name}: </font>'
                     f'<font name="{link_font_name}" size="{link_font_size}" color="{link_color_hex}">'
                     f'{hyperlink_text}</font>'
                 )
                # Need a combined style or use the heading style
                combined_style = ParagraphStyle('combined_project_style', parent=heading_style)
                row_index = self._add_table_row(
                    table_data=table_data, table_styles=table_styles, row_index=row_index,
                    content_style_map=[
                        (paragraph_text, combined_style),
                        (duration, resume_pdf_styles.PARAGRAPH_STYLES.get("company_duration")),
                    ],
                )

            else:
                # Row without link
                 row_index = self._add_table_row(
                    table_data=table_data, table_styles=table_styles, row_index=row_index,
                    content_style_map=[
                        (project_name, heading_style),
                        (duration, resume_pdf_styles.PARAGRAPH_STYLES.get("company_duration")),
                    ],
                )


            # Description and Highlights (Treat description as a bullet point if highlights missing)
            content_list = project.highlights or []
            if not content_list and project.description:
                content_list = [project.description]

            for i, item in enumerate(content_list):
                clean_item = item.replace("'", "").replace('"', "").strip() if item else ""
                style = (
                    resume_pdf_styles.PARAGRAPH_STYLES.get("last_bullet_point")
                    if i == len(content_list) - 1
                    else resume_pdf_styles.PARAGRAPH_STYLES.get("bullet_points")
                )
                padding = (5, 1) if i == len(content_list) - 1 else (0, 1)

                row_index = self._add_table_row(
                    table_data=table_data, table_styles=table_styles, bullet_point="•", row_index=row_index,
                    content_style_map=[(clean_item, style)],
                    span=True, padding=padding,
                )

        return row_index


    def add_education(self, table_data, table_styles, row_index, education: Optional[List[EducationItem]]):
        """Add education section."""
        if not education:
            return row_index

        row_index = self._add_table_row(
            table_data=table_data, table_styles=table_styles, row_index=row_index,
            content_style_map=[("Education", resume_pdf_styles.PARAGRAPH_STYLES.get("section"))],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for edu in education:
            # Combine degree info
            degree_info = f"{edu.studyType or ''} in {edu.area or 'N/A'}"
            # Format dates
            start_date_str = edu.startDate or "?"
            end_date_str = edu.endDate or "Present"
            duration = f"{start_date_str} - {end_date_str}"

            # Institution Row
            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[
                    (edu.institution or "N/A", resume_pdf_styles.PARAGRAPH_STYLES.get("company_heading")), # Reuse style
                    (duration, resume_pdf_styles.PARAGRAPH_STYLES.get("company_duration")),
                ],
            )

            # Degree Row
            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[
                    (degree_info, resume_pdf_styles.PARAGRAPH_STYLES.get("education")),
                    (f"GPA: {edu.score}" if edu.score else "", resume_pdf_styles.PARAGRAPH_STYLES.get("company_location")), # Reuse style, align right
                ],
                 padding=(5, 1) # Add padding after degree info
            )

            # Optional: Add courses if present
            if edu.courses:
                 courses_str = "Relevant Courses: " + ", ".join(edu.courses)
                 row_index = self._add_table_row(
                    table_data=table_data, table_styles=table_styles, row_index=row_index,
                    content_style_map=[(courses_str, resume_pdf_styles.PARAGRAPH_STYLES.get("bullet_points"))], # Reuse bullet style
                    span=True, padding=(5,1)
                 )


        return row_index

    def add_skills(self, table_data, table_styles, row_index, skills: Optional[List[SkillItem]]):
        """Add skills section."""
        if not skills:
            return row_index

        row_index = self._add_table_row(
            table_data=table_data, table_styles=table_styles, row_index=row_index,
            content_style_map=[("Skills", resume_pdf_styles.PARAGRAPH_STYLES.get("section"))],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for skill_item in skills:
            category = skill_item.category or "General"
            skills_list = skill_item.skills or []
            skills_str = ", ".join(skills_list)
            # Use bold font name defined in styles
            bold_font = resume_pdf_styles.FONT_NAMES.get('bold', 'Helvetica-Bold')
            formatted_skills = f"<font name='{bold_font}'>{category}</font>: {skills_str}"

            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[(formatted_skills, resume_pdf_styles.PARAGRAPH_STYLES.get("skills"))],
                span=True, padding=(2, 2),
            )
        return row_index

    def _clean_url(self, url: Optional[str]) -> str:
        if not url:
            return ""
        return url.replace("https://", "").replace("http://", "").replace("www.", "")

    def generate_resume_pdf(self, resume_data: StructuredResume, output_dir: str) -> str:
        """
        Generate a resume PDF from a StructuredResume object.

        Args:
            resume_data (StructuredResume): The Pydantic object containing resume information.
            output_dir (str): The directory where the PDF will be saved.

        Returns:
            str: The full path to the generated PDF file.
        """
        if not resume_data or not resume_data.basic:
            raise ValueError("Basic resume information is missing.")

        basic_info = resume_data.basic
        name = basic_info.name or "Unnamed Resume"
        pdf_filename = f"{name.replace(' ', '_')}_resume_{Path(tempfile.NamedTemporaryFile().name).stem}.pdf"
        output_path = os.path.join(output_dir, pdf_filename)

        doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)

        table_data = []
        table_styles = []
        row_index = 0

        # Optional Debug Grid
        # table_styles.append(resume_pdf_styles.DEBUG_STYLE)

        # Document Alignment (Center headers)
        table_styles.extend(resume_pdf_styles.DOCUMENT_ALIGNMENT)

        # --- Header Section ---
        # Name
        row_index = self._add_table_row(
            table_data=table_data, table_styles=table_styles, row_index=row_index,
            content_style_map=[(name, resume_pdf_styles.PARAGRAPH_STYLES.get("name"))],
            span=True,
        )

        # Contact Info Line
        contact_parts = [
            basic_info.email,
            basic_info.phone,
            f'<a href="{basic_info.linkedin_url}">{self._clean_url(basic_info.linkedin_url)}</a>' if basic_info.linkedin_url else None,
            f'<a href="{basic_info.github_url}">{self._clean_url(basic_info.github_url)}</a>' if basic_info.github_url else None,
            f'<a href="{basic_info.portfolio_url}">{self._clean_url(basic_info.portfolio_url)}</a>' if basic_info.portfolio_url else None,
            basic_info.location,
        ]
        contact_info = " | ".join(filter(None, contact_parts))

        row_index = self._add_table_row(
            table_data=table_data, table_styles=table_styles, row_index=row_index,
            content_style_map=[(contact_info, resume_pdf_styles.PARAGRAPH_STYLES.get("contact"))],
            span=True,
        )

        # --- Objective Section ---
        if resume_data.objective:
            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[("Objective", resume_pdf_styles.PARAGRAPH_STYLES.get("section"))],
                span=True, padding=(1, 5) # Add padding before section
            )
            self._append_section_table_style(table_styles, row_index - 1)

            row_index = self._add_table_row(
                table_data=table_data, table_styles=table_styles, row_index=row_index,
                content_style_map=[(resume_data.objective, resume_pdf_styles.PARAGRAPH_STYLES.get("objective"))],
                span=True, padding=(5, 1) # Add padding after objective
            )

        # --- Other Sections ---
        row_index = self.add_experiences(table_data, table_styles, row_index, resume_data.experiences)
        row_index = self.add_projects(table_data, table_styles, row_index, resume_data.projects)
        row_index = self.add_education(table_data, table_styles, row_index, resume_data.education)
        row_index = self.add_skills(table_data, table_styles, row_index, resume_data.skills)

        # --- Build Table ---
        table = Table(
            table_data,
            colWidths=[
                resume_pdf_styles.FULL_COLUMN_WIDTH * 0.7, # Main content
                resume_pdf_styles.FULL_COLUMN_WIDTH * 0.3, # Dates/Location (right aligned)
            ],
            spaceBefore=0,
            spaceAfter=0,
        )
        table.setStyle(TableStyle(table_styles))

        # --- Build PDF Document ---
        try:
             logger.info(f"Building PDF document at: {output_path}")
             doc.build([table])
             logger.info(f"Successfully generated resume PDF: {output_path}")
             return output_path
        except Exception as e:
             logger.error(f"Failed to build PDF document: {e}", exc_info=True)
             raise # Re-raise the exception after logging

# Example Usage (for testing if run directly)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing PDF Generation Service...")

    # Create dummy StructuredResume data
    test_resume = StructuredResume(
        basic=BasicInfo(
            name="Jane Doe",
            email="jane.doe@email.com",
            phone="123-456-7890",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/janedoe",
            github_url="https://github.com/janedoe"
        ),
        objective="Highly motivated software engineer seeking a challenging role in backend development.",
        experiences=[
            ExperienceItem(company="Tech Corp", position="Software Engineer", startDate="2020-01", endDate="Present", highlights=["Developed feature X", "Improved performance by Y%"]),
            ExperienceItem(company="Startup Inc", position="Junior Developer", startDate="2018-06", endDate="2019-12", highlights=["Built API Z", "Fixed bug Q"])
        ],
        projects=[
            ProjectItem(name="Personal Website", url="https://janedoe.dev", startDate="2022", description="My personal portfolio website.", highlights=["Used React and FastAPI"])
        ],
        education=[
            EducationItem(institution="State University", area="Computer Science", studyType="Bachelor of Science", startDate="2014", endDate="2018", score="3.8/4.0")
        ],
        skills=[
            SkillItem(category="Programming Languages", skills=["Python", "Java", "JavaScript"]),
            SkillItem(category="Frameworks", skills=["FastAPI", "React", "Spring Boot"]),
            SkillItem(category="Databases", skills=["PostgreSQL", "MongoDB"])
        ]
    )

    generator = StructuredResumePdfGenerator()
    temp_dir = tempfile.gettempdir()
    try:
        pdf_path = generator.generate_resume_pdf(test_resume, temp_dir)
        logger.info(f"Test PDF generated at: {pdf_path}")
        # Optionally open the PDF here for verification if needed
        # import subprocess
        # subprocess.run(['open', pdf_path], check=True) # macOS example
    except Exception as e:
        logger.error(f"Error during test generation: {e}")