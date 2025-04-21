import logging
import re
from typing import List, Dict, Any, Optional # Added Optional

from ..schemas.resume import PdfTextItem, StructuredResume, BasicInfo, EducationItem, ExperienceItem, ProjectItem, SkillItem
from collections import Counter
import statistics

import openai # Added
from ..core.config import settings # Added

# TODO: Import necessary LangChain components (ChatPromptTemplate, LLM, output parsers)

logger = logging.getLogger(__name__)

# Initialize Azure OpenAI Client
if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
    logger.info("Initializing Azure OpenAI client...")
    azure_llm = openai.AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        # Note: Deployment name is usually passed during the API call (e.g., client.chat.completions.create(model=settings.AZURE_OPENAI_DEPLOYMENT_NAME, ...))
    )
    logger.info("Azure OpenAI client initialized.")
else:
    logger.warning("Azure OpenAI credentials not found in settings. LLM features will be disabled.")
    azure_llm = None


# --- Helper Functions ---

# Constants for preprocessing
Y_TOLERANCE_FACTOR = 0.5 # Allow lines whose y-coords differ by this factor of the item height

# Constants for section identification
# Simple keyword matching (case-insensitive, allow variations)
SECTION_KEYWORDS = {
    "objective": [r"objective", r"summary", r"profile"],
    "experience": [r"experience", r"employment history", r"work history", r"professional experience"],
    "education": [r"education", r"academic background"],
    "projects": [r"projects", r"personal projects"],
    "skills": [r"skills", r"technical skills", r"competencies", r"proficiencies"],
    # Contact info is usually at the top and doesn't have a standard heading
}

def is_likely_heading(line: Dict[str, Any], avg_height: float) -> bool:
    """Check if a line looks like a heading based on formatting."""
    is_larger = line.get("height", 0) > avg_height * 1.1
    is_all_caps = line.get("text", "").isupper() and len(line.get("text", "")) > 1
    is_boldish = "bold" in line.get("fontName", "").lower()
    return (is_larger or is_all_caps) or (is_boldish and (is_larger or is_all_caps))


def preprocess_text_items(text_items: List[PdfTextItem]) -> List[Dict[str, Any]]:
    """
    Groups text items into lines based on coordinates and sorts them logically.
    Returns a list of dictionaries, each representing a line with combined text and style info.
    """
    if not text_items:
        return []
    logger.info(f"Preprocessing {len(text_items)} text items...")
    text_items.sort(key=lambda item: (item.transform[5], item.transform[4]))
    processed_lines = []
    current_line_items: List[PdfTextItem] = []
    for item in text_items:
        if not item.str or item.str.isspace(): continue
        item_y = item.transform[5]
        item_height = item.height
        if not current_line_items:
            current_line_items.append(item)
        else:
            current_line_y = current_line_items[0].transform[5]
            y_tolerance = current_line_items[0].height * Y_TOLERANCE_FACTOR
            if abs(item_y - current_line_y) <= y_tolerance:
                current_line_items.append(item)
            else:
                current_line_items.sort(key=lambda i: i.transform[4])
                line_text = " ".join(i.str.strip() for i in current_line_items if i.str)
                if line_text:
                    line_y = statistics.mean(i.transform[5] for i in current_line_items)
                    line_x = min(i.transform[4] for i in current_line_items)
                    line_height = statistics.mean(i.height for i in current_line_items)
                    font_counts = Counter(i.fontName for i in current_line_items)
                    dominant_font = font_counts.most_common(1)[0][0] if font_counts else "Unknown"
                    processed_lines.append({
                        "text": line_text, "y": line_y, "x": line_x, "height": line_height,
                        "fontName": dominant_font, "_items": [item.model_dump() for item in current_line_items]
                    })
                current_line_items = [item]
    if current_line_items:
        current_line_items.sort(key=lambda i: i.transform[4])
        line_text = " ".join(i.str.strip() for i in current_line_items if i.str)
        if line_text:
            line_y = statistics.mean(i.transform[5] for i in current_line_items)
            line_x = min(i.transform[4] for i in current_line_items)
            line_height = statistics.mean(i.height for i in current_line_items)
            font_counts = Counter(i.fontName for i in current_line_items)
            dominant_font = font_counts.most_common(1)[0][0] if font_counts else "Unknown"
            processed_lines.append({
                "text": line_text, "y": line_y, "x": line_x, "height": line_height,
                "fontName": dominant_font, "_items": [item.model_dump() for item in current_line_items]
            })
    logger.info(f"Preprocessing complete. Generated {len(processed_lines)} lines.")
    return processed_lines

def identify_sections(processed_lines: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Identifies logical sections based on keyword matching and simple formatting heuristics.
    """
    logger.info("Identifying sections...")
    sections = { "contact": [], "objective": [], "experience": [], "education": [], "projects": [], "skills": [], "unknown": [] }
    if not processed_lines:
        logger.warning("No processed lines to identify sections from.")
        return sections
    avg_height = statistics.mean(line.get("height", 0) for line in processed_lines if line.get("height", 0) > 0) if processed_lines else 0
    current_section = "unknown"
    for line in processed_lines:
        line_text_lower = line.get("text", "").lower().strip()
        matched_section = None
        for section_name, keywords in SECTION_KEYWORDS.items():
            for keyword_pattern in keywords:
                if re.search(r'\b' + keyword_pattern + r'\b', line_text_lower, re.IGNORECASE):
                     if is_likely_heading(line, avg_height) or len(line_text_lower.split()) <= 3:
                        matched_section = section_name
                        break
            if matched_section: break
        if matched_section:
            current_section = matched_section
            logger.debug(f"Identified section '{current_section}' at line: '{line.get('text')}'")
        else:
            sections[current_section].append(line)

    # Post-processing for contact info
    potential_contact_section = "unknown" if sections["unknown"] else None
    if not potential_contact_section and sections["contact"]: # If contact was explicitly tagged
        potential_contact_section = "contact"
    elif sections["unknown"]: # Check if unknown appears first
         first_unknown_y = sections["unknown"][0]['y'] if sections["unknown"] else float('inf')
         first_other_y = min((sections[s][0]['y'] for s in sections if s != "unknown" and sections[s]), default=float('inf'))
         if first_unknown_y < first_other_y:
             potential_contact_section = "unknown"
         else: # If unknown is not first, keep it as unknown unless empty
             if not sections["unknown"]: potential_contact_section = None

    if potential_contact_section and potential_contact_section != "contact":
        logger.info(f"Assuming '{potential_contact_section}' section lines are contact info.")
        sections["contact"].extend(sections.pop(potential_contact_section, []))
        # Ensure the key exists before deleting
        if potential_contact_section in sections:
            del sections[potential_contact_section]
        # Create unknown section if it doesn't exist after potential pop
        if "unknown" not in sections:
             sections["unknown"] = []


    logger.info(f"Section identification complete. Sections found: { {k: len(v) for k, v in sections.items() if v} }")
    return sections

# --- Regex Patterns for Extraction ---
# Basic patterns, can be improved significantly
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
LINKEDIN_REGEX = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?')

# --- Extraction Helper Functions ---

def _find_first_match(lines: List[Dict[str, Any]], regex: re.Pattern) -> Optional[str]:
    """Find the first match of a regex in a list of lines."""
    for line in lines:
        match = regex.search(line.get("text", ""))
        if match:
            return match.group(0).strip()
    return None

def _extract_name(lines: List[Dict[str, Any]]) -> Optional[str]:
    """Extract name, often the first or second line with largest font."""
    if not lines: return None
    # Sort by font size (height) desc, then position asc
    lines.sort(key=lambda l: (-l.get("height", 0), l.get("y", 0), l.get("x", 0)))
    # Check top few lines for something that looks like a name
    for i in range(min(3, len(lines))): # Check top 3 lines
        text = lines[i].get("text", "").strip()
        # Simple check: At least two words, capitalized, not purely contact info?
        words = text.split()
        if (len(words) >= 2 and
            all(word[0].isupper() for word in words if word) and
            not EMAIL_REGEX.search(text) and
            not PHONE_REGEX.search(text) and
            not LINKEDIN_REGEX.search(text) and
            len(text) < 50): # Avoid long sentences
                 return text
    logger.warning("Could not reliably identify name in contact section.")
    return None # Fallback

def _extract_skills(lines: List[Dict[str, Any]]) -> List[SkillItem]:
    """Extract skills, potentially handling categories (basic)."""
    skills_list: List[SkillItem] = []
    current_category = "General"

    # Simple approach: split lines by common delimiters like ',', ';', '|', or bullets '•●*'
    # More advanced: Look for lines ending in ':' as category headers.

    for line in lines:
        text = line.get("text", "").strip()
        if not text: continue

        # Basic category detection (line ending with ':')
        if text.endswith(':') and len(text) < 50: # Avoid long lines ending in ':'
            current_category = text[:-1].strip()
            logger.debug(f"Detected skills category: {current_category}")
            continue # Don't add the category header itself as a skill

        # Split potential skills within the line
        # Replace common bullets with a standard delimiter (comma) for splitting
        text = re.sub(r'[•●*]\s+', ', ', text)
        # Split by comma, semicolon, or pipe
        potential_skills = re.split(r'[,;|\n]+', text)

        for skill_name in potential_skills:
            skill_name = skill_name.strip()
            # Basic filtering: non-empty, not just punctuation, reasonable length
            if skill_name and len(skill_name) > 1 and len(skill_name) < 50 and not re.fullmatch(r'[^a-zA-Z0-9\s]+', skill_name): # Allow spaces within skill name
                 # Avoid adding duplicates within the same category (case-insensitive check)
                 if not any(s.name.lower() == skill_name.lower() and s.category.lower() == current_category.lower() for s in skills_list):
                     skills_list.append(SkillItem(name=skill_name, category=current_category))

    if not skills_list:
        logger.warning("No skills extracted. The format might be unrecognized.")

    return skills_list


def extract_structured_data(sections: Dict[str, List[Dict[str, Any]]]) -> StructuredResume:
    """
    Parses the lines within each identified section into the structured Pydantic models.
    Currently implements basic extraction for Contact Info, Objective, and Skills.
    """
    logger.info("Extracting structured data from sections...")

    contact_lines = sections.get("contact", [])
    skill_lines = sections.get("skills", [])
    objective_lines = sections.get("objective", []) # Basic objective handling
    # TODO: Get lines for other sections when implemented

    # --- Extract Basic Info ---
    # Make a copy to avoid modifying the original section data if helpers sort/mutate
    contact_lines_copy = [line.copy() for line in contact_lines]
    name = _extract_name(contact_lines_copy) # _extract_name sorts the copy
    email = _find_first_match(contact_lines, EMAIL_REGEX)
    phone = _find_first_match(contact_lines, PHONE_REGEX)
    linkedin = _find_first_match(contact_lines, LINKEDIN_REGEX)
    # TODO: Extract location, portfolio/website etc.

    basic_info = BasicInfo(
        name=name,
        email=email,
        phone=phone,
        linkedin_url=linkedin,
        # location=None, # Add when implemented
        # website=None, # Add when implemented
    )

    # --- Extract Objective/Summary ---
    # Very basic: concatenate lines in the objective section
    objective = " ".join(line.get("text", "") for line in objective_lines).strip() if objective_lines else None

    # --- Extract Skills ---
    skills = _extract_skills(skill_lines)

    # --- TODO: Extract Education, Experience, Projects ---
    education = []
    experiences = []
    projects = []

    structured_data = StructuredResume(
        basic=basic_info,
        objective=objective,
        education=education,
        experiences=experiences,
        projects=projects,
        skills=skills
    )

    logger.info("Structured data extraction complete (basic implementation for contact, objective, skills).")
    return structured_data

def tailor_content(structured_data: StructuredResume, job_description: str) -> StructuredResume:
    """
    Uses an LLM to tailor specific parts of the resume based on the job description.
    - Rewrites Objective/Summary
    - Selects/Keywords relevant Skills
    - Rewrites Experience/Project highlights
    """
    # TODO: Implement LLM calls for skills matching, experience/project highlight rewriting.
    # TODO: Consider using LangChain for more complex prompt management and output parsing.
    logger.info("Tailoring objective using Azure LLM...")

    if not azure_llm or not settings.AZURE_OPENAI_DEPLOYMENT_NAME:
        logger.warning("Azure LLM client or deployment name not configured. Skipping tailoring.")
        return structured_data

    try:
        # --- Tailor Objective ---
        current_objective = structured_data.objective or "No objective provided."
        system_prompt = "You are an expert resume writer. Rewrite the provided resume objective/summary to be concise, impactful, and highly relevant to the target job description. Focus on aligning the candidate's key qualifications with the job requirements."
        user_prompt = f"""
        Rewrite the following resume objective/summary based on the target job description.

        Current Objective/Summary:
        ---
        {current_objective}
        ---

        Target Job Description:
        ---
        {job_description}
        ---

        Rewritten Objective/Summary (Return ONLY the rewritten text):
        """

        response = azure_llm.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME, # Specify the deployment name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        if response.choices and response.choices[0].message and response.choices[0].message.content:
            tailored_objective = response.choices[0].message.content.strip()
            structured_data.objective = tailored_objective
            logger.info(f"Successfully tailored objective.")
        else:
            logger.warning("LLM response for objective tailoring was empty or invalid.")

        # --- TODO: Tailor Skills (e.g., select top N skills matching JD) ---
        # --- TODO: Tailor Experiences/Projects (e.g., rewrite bullet points) ---

    except openai.APIError as e:
        logger.error(f"Azure OpenAI API returned an API Error: {e}")
    except openai.APIConnectionError as e:
        logger.error(f"Failed to connect to Azure OpenAI API: {e}")
    except openai.RateLimitError as e:
        logger.error(f"Azure OpenAI API request exceeded rate limit: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM tailoring: {e}", exc_info=True)


    logger.info("Content tailoring attempt complete.")
    return structured_data

# --- Main Service Function ---

def process_and_tailor_resume(
    text_items: List[PdfTextItem],
    job_description: str | None = None
) -> StructuredResume:
    """
    Orchestrates the resume processing and tailoring workflow.
    """
    logger.info("Starting resume processing and tailoring...")

    # 1. Preprocess text items into lines
    processed_lines = preprocess_text_items(text_items)
    if not processed_lines:
         # Handle case with no processable lines
         logger.warning("No processable lines found after preprocessing.")
         # Return empty or minimal structure
         return StructuredResume(basic=BasicInfo(), objective="Could not process resume content.")

    # 2. Identify logical sections
    sections = identify_sections(processed_lines)

    # 3. Extract structured data from sections
    structured_data = extract_structured_data(sections)

    # 4. Tailor content using LLM (if job description is provided)
    if job_description and structured_data:
        structured_data = tailor_content(structured_data, job_description)
    elif not job_description:
        logger.info("No job description provided, skipping LLM tailoring.")

    logger.info("Resume processing and tailoring finished.")
    return structured_data