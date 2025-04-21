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


# --- LLM Helper ---

def _call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 200) -> Optional[str]:
    """Helper function to call the Azure OpenAI API."""
    if not azure_llm or not settings.AZURE_OPENAI_DEPLOYMENT_NAME:
        logger.warning("Azure LLM client or deployment name not configured. Cannot call LLM.")
        return None

    try:
        logger.debug(f"Calling LLM. System Prompt: {system_prompt[:100]}... User Prompt: {user_prompt[:100]}...")
        response = azure_llm.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        if response.choices and response.choices[0].message and response.choices[0].message.content:
            logger.debug("LLM call successful.")
            return response.choices[0].message.content.strip()
        else:
            logger.warning("LLM response was empty or invalid.")
            return None

    except openai.APIError as e:
        logger.error(f"Azure OpenAI API returned an API Error: {e}")
    except openai.APIConnectionError as e:
        logger.error(f"Failed to connect to Azure OpenAI API: {e}")
    except openai.RateLimitError as e:
        logger.error(f"Azure OpenAI API request exceeded rate limit: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM call: {e}", exc_info=True)

    return None


# --- Preprocessing & Section Identification Helpers ---

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

def is_likely_heading(line: Dict[str, Any], avg_height: float, max_words_for_heading: int = 5) -> bool:
    """Check if a line looks like a heading based on formatting and length."""
    text = line.get("text", "").strip()
    words = text.split()
    word_count = len(words)

    # Rule 1: Font size significantly larger than average
    is_significantly_larger = line.get("height", 0) > avg_height * 1.15 # Increased threshold

    # Rule 2: All caps (and not just a single letter/symbol)
    is_all_caps = text.isupper() and word_count > 0 and len(text) > 1

    # Rule 3: Boldish font style
    is_boldish = "bold" in line.get("fontName", "").lower()

    # Rule 4: Short line (potentially a heading)
    is_short_line = word_count <= max_words_for_heading

    # Rule 5: Title Case (most words capitalized, not all caps)
    # Handles cases like "Professional Experience" which might not be bold or larger
    is_title_case = (
        word_count > 0 and
        not is_all_caps and
        sum(1 for word in words if word and word[0].isupper()) / word_count >= 0.7 # High proportion capitalized
    )

    # Combine rules:
    # - Strong indicators: Significantly larger font OR all caps.
    # - Supporting indicators: Bold font, title case, short line length.
    # A line is likely a heading if it has strong indicators OR
    # if it's short and has supporting indicators (bold or title case).
    is_strong_indicator = is_significantly_larger or is_all_caps
    is_supporting_indicator = is_boldish or is_title_case

    likely = is_strong_indicator or (is_short_line and is_supporting_indicator)
    # logger.debug(f"is_likely_heading('{text[:30]}...'): larger={is_significantly_larger}, allcaps={is_all_caps}, bold={is_boldish}, short={is_short_line}, title={is_title_case} -> {likely}")
    return likely


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
    possible_heading_indices = {i for i, line in enumerate(processed_lines) if is_likely_heading(line, avg_height)}
    current_section = "unknown" # Start with unknown, assume contact info is first unless a heading found early

    for i, line in enumerate(processed_lines):
        line_text = line.get("text", "").strip()
        line_text_lower = line_text.lower()
        word_count = len(line_text.split())
        matched_section = None

        is_potential_heading_line = i in possible_heading_indices

        # Check for keyword match only if it looks like a heading or is a very short line
        if is_potential_heading_line or word_count <= 5:
            for section_name, keywords in SECTION_KEYWORDS.items():
                for keyword_pattern in keywords:
                    # Use regex that matches the whole line or the pattern as a standalone phrase
                    # Check if the line *mostly* consists of the keyword pattern
                    # This is still heuristic, might need adjustment
                    if re.fullmatch(r'\s*' + keyword_pattern + r'\s*[:.]?', line_text_lower, re.IGNORECASE):
                        matched_section = section_name
                        break
                    # Allow if keyword is present and it's considered a heading format
                    elif is_potential_heading_line and re.search(r'\b' + keyword_pattern + r'\b', line_text_lower, re.IGNORECASE):
                         matched_section = section_name
                         break # Found a potential match
                if matched_section:
                    break # Found keyword for this section

        if matched_section:
            # If we switch section, assign the matched line as the heading (don't add to previous section)
            current_section = matched_section
            logger.debug(f"Identified section heading '{current_section}' at line {i}: '{line.get('text')}'")
            # Don't append the heading line itself to the previous section's content
        else:
            # If it wasn't identified as a heading, add it to the current section's content
            sections[current_section].append(line)

    # Refined Post-processing for contact info
    # If the first few lines were put in "unknown" and contain contact patterns, move them to "contact"
    if sections["unknown"]:
        moved_contact_lines = []
        remaining_unknown = []
        lines_to_check = min(5, len(sections["unknown"])) # Check first 5 unknown lines
        contains_contact_pattern = False
        for i in range(len(sections["unknown"])):
            line_text = sections["unknown"][i].get("text", "")
            if i < lines_to_check and (EMAIL_REGEX.search(line_text) or PHONE_REGEX.search(line_text) or LINKEDIN_REGEX.search(line_text)):
                 contains_contact_pattern = True

            if i < lines_to_check and contains_contact_pattern:
                 # If we found a pattern within the first few lines, assume this block is contact info
                 moved_contact_lines.append(sections["unknown"][i])
            else:
                 remaining_unknown.append(sections["unknown"][i])

        if moved_contact_lines:
            logger.info(f"Moving {len(moved_contact_lines)} lines from 'unknown' to 'contact' based on pattern matching.")
            sections["contact"].extend(moved_contact_lines)
            sections["unknown"] = remaining_unknown


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
    experience_lines = sections.get("experience", [])
    education_lines = sections.get("education", [])
    project_lines = sections.get("projects", []) # Keep placeholder for now

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

    # --- Extract Education ---
    education = _extract_education(education_lines)

    # --- Extract Experience ---
    experiences = _extract_experience(experience_lines)

    # --- TODO: Extract Projects ---
    projects = [] # Placeholder for projects

    structured_data = StructuredResume(
        basic=basic_info,
        objective=objective,
        education=education,
        experiences=experiences,
        projects=projects,
        skills=skills
    )

    logger.info(f"Structured data extraction complete. Found: {len(education)} education, {len(experiences)} experience entries.")
    return structured_data

# --- Experience/Education/Project Extraction Helpers ---

# Very basic date range regex (YYYY-YYYY, Month YYYY - Month YYYY, Month YYYY - Present)
# Needs significant improvement for robustness (e.g., handling seasons, various separators)
DATE_RANGE_REGEX = re.compile(
    r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b)\s*[-–—to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)\b' +
    r'|(\b\d{4}\b)\s*[-–—to]+\s*(\b\d{4}|Present|Current)\b' +
    r'|(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b' # Single date (graduation?)
    , re.IGNORECASE
)
# Simple bullet point start
BULLET_POINT_REGEX = re.compile(r'^\s*[-•*–—]\s+')

def _extract_experience(lines: List[Dict[str, Any]]) -> List[ExperienceItem]:
    """Very basic rule-based extraction for experience section."""
    experiences: List[ExperienceItem] = []
    if not lines: return experiences

    current_experience: Optional[ExperienceItem] = None
    current_description_lines: List[str] = []

    for i, line in enumerate(lines):
        text = line.get("text", "").strip()
        if not text: continue

        date_match = DATE_RANGE_REGEX.search(text)
        is_bullet = BULLET_POINT_REGEX.match(text)

        # Heuristic: If a line contains a date range and isn't clearly just a description bullet,
        # assume it *might* be the start (or part of the header) of a new role.
        # This logic is very naive and needs improvement.
        is_likely_role_header = date_match is not None and not is_bullet

        # If we detect a potential new role header and we were processing a previous role
        if is_likely_role_header and current_experience:
             # Finalize the previous experience item
            current_experience.description = "\n".join(current_description_lines).strip()
            experiences.append(current_experience)
            current_experience = None
            current_description_lines = []

        # If it's likely a new role header line (or we haven't started one yet)
        if is_likely_role_header or not current_experience:
            # Try to extract details from this line and potentially the previous one
            # This needs more sophisticated logic to reliably find Title, Company, Location, Dates
            title = "Unknown Title" # Placeholder
            company = "Unknown Company" # Placeholder
            location = None # Placeholder
            dates = date_match.group(0).strip() if date_match else None

            # Example: Check previous line if current looks just like dates/location
            if i > 0 and (len(text.split()) < 5 or date_match): # If current line is short/has date
                prev_text = lines[i-1].get("text","").strip()
                # Maybe prev line had Title/Company? Very rough guess.
                if len(prev_text.split()) > 1 and len(prev_text) < 70:
                    # Simplistic split: assume first part is title, rest is company? Needs work!
                    parts = prev_text.split(' at ') # Common separator
                    if len(parts) == 2:
                        title = parts[0].strip()
                        company = parts[1].strip()
                    else:
                         parts = prev_text.split(',') # Another possibility
                         if len(parts) >= 2:
                            title = parts[0].strip()
                            company = parts[1].strip()
                         else: # Fallback
                             title = prev_text # Assume previous line was title/company combined

            # Create a new experience item (even if details are placeholders)
            current_experience = ExperienceItem(
                title=title,
                company=company,
                location=location,
                dates=dates,
                description="" # Will be filled by bullets
            )
            current_description_lines = [] # Reset descriptions

        # If it's likely a description bullet point and we have an active role
        elif is_bullet and current_experience:
            current_description_lines.append(BULLET_POINT_REGEX.sub("", text)) # Add text without bullet

        # Otherwise, assume it's part of the description for the current role
        elif current_experience:
             current_description_lines.append(text)

    # Add the last processed experience item
    if current_experience:
        current_experience.description = "\n".join(current_description_lines).strip()
        experiences.append(current_experience)

    logger.info(f"Extracted {len(experiences)} potential experience entries (basic rules).")
    return experiences


def _extract_education(lines: List[Dict[str, Any]]) -> List[EducationItem]:
    """Very basic rule-based extraction for education section."""
    education_list: List[EducationItem] = []
    if not lines: return education_list

    # Similar naive approach to experience - look for date ranges as potential separators
    # Assume lines between date ranges belong to one entry.
    entry_lines: List[str] = []
    for line in lines:
        text = line.get("text", "").strip()
        if not text: continue
        entry_lines.append(text)
        date_match = DATE_RANGE_REGEX.search(text)
        # If a date is found, assume end of an entry (needs refinement)
        if date_match:
            if entry_lines:
                # Very basic parsing of collected lines for one entry
                degree = entry_lines[0] # Guess: First line is degree
                institution = entry_lines[1] if len(entry_lines) > 1 else "Unknown Institution" # Guess: Second is institution
                dates = date_match.group(0).strip()
                # TODO: Extract location, GPA, details from other lines
                details = "\n".join(entry_lines[2:]) # Rest are details?
                education_list.append(EducationItem(
                    institution=institution,
                    degree=degree,
                    dates=dates,
                    details=details if details else None
                ))
                entry_lines = [] # Reset for next entry

    # Process any remaining lines as a potential last entry
    if entry_lines:
         degree = entry_lines[0]
         institution = entry_lines[1] if len(entry_lines) > 1 else "Unknown Institution"
         # Try finding date in the last line if not found before
         dates = None
         if len(entry_lines) > 0:
             last_line_match = DATE_RANGE_REGEX.search(entry_lines[-1])
             if last_line_match:
                 dates = last_line_match.group(0).strip()
         details = "\n".join(entry_lines[2:])
         education_list.append(EducationItem(
                institution=institution,
                degree=degree,
                dates=dates,
                details=details if details else None
            ))


    logger.info(f"Extracted {len(education_list)} potential education entries (basic rules).")
    return education_list


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
        obj_system_prompt = "You are an expert resume writer. Rewrite the provided resume objective/summary to be concise, impactful, and highly relevant to the target job description. Focus on aligning the candidate's key qualifications with the job requirements."
        obj_user_prompt = f"""Rewrite the following resume objective/summary based on the target job description.

Current Objective/Summary:
---
{current_objective}
---

Target Job Description:
---
{job_description}
---

Rewritten Objective/Summary (Return ONLY the rewritten text):"""

        tailored_objective = _call_llm(obj_system_prompt, obj_user_prompt, max_tokens=150)
        if tailored_objective:
            structured_data.objective = tailored_objective
            logger.info("Successfully tailored objective.")
        else:
            logger.warning("Failed to tailor objective or LLM response was empty.")


        # --- Tailor Skills ---
        logger.info("Tailoring skills using Azure LLM...")
        if structured_data.skills:
            current_skills_str = ", ".join([skill.name for skill in structured_data.skills])
            skills_system_prompt = "You are a resume analysis assistant. Analyze the provided skill list and the target job description. Identify and return ONLY a comma-separated list of the most relevant skills from the original list that align strongly with the job requirements. Prioritize skills explicitly mentioned or strongly implied in the job description."
            skills_user_prompt = f"""Analyze the following list of skills based on the target job description and return a comma-separated list of the most relevant skills.

Current Skills:
---
{current_skills_str}
---

Target Job Description:
---
{job_description}
---

Most Relevant Skills (Return ONLY a comma-separated list):"""

            tailored_skills_str = _call_llm(skills_system_prompt, skills_user_prompt, max_tokens=200)
            if tailored_skills_str:
                # Parse the response and update the skills list
                relevant_skill_names = [s.strip() for s in tailored_skills_str.split(',') if s.strip()]
                # Replace original skills with the tailored list (simple approach)
                structured_data.skills = [SkillItem(name=name, category="Relevant Skills") for name in relevant_skill_names]
                logger.info(f"Successfully tailored skills. Identified {len(structured_data.skills)} relevant skills.")
            else:
                logger.warning("Failed to tailor skills or LLM response was empty.")
        else:
            logger.info("No skills found in structured data to tailor.")


        # --- Tailor Experiences ---
        logger.info("Tailoring experience descriptions using Azure LLM...")
        if structured_data.experiences:
            updated_experiences = []
            for i, exp in enumerate(structured_data.experiences):
                logger.info(f"Tailoring experience item {i+1}/{len(structured_data.experiences)}: {exp.title} at {exp.company}")
                current_desc = exp.description or "No description provided."
                if not current_desc or current_desc == "No description provided.":
                     logger.warning(f"Skipping experience item {i+1} due to missing description.")
                     updated_experiences.append(exp) # Keep original if no description
                     continue

                exp_system_prompt = "You are an expert resume writer specializing in tailoring experience bullet points. Rewrite the provided bullet points to highlight achievements and responsibilities most relevant to the target job description, using action verbs and quantifying results where possible. Maintain the original number of bullet points if feasible."
                exp_user_prompt = f"""Rewrite the following experience bullet points to strongly align with the target job description. Focus on keywords, required skills, and desired outcomes mentioned in the job description.

Original Bullet Points (separated by newline):
---
{current_desc}
---

Target Job Description:
---
{job_description}
---

Rewritten Bullet Points (Return ONLY the rewritten bullet points, separated by newline):"""

                # Use slightly higher temperature for more creative rewriting, adjust tokens based on expected length
                tailored_desc = _call_llm(exp_system_prompt, exp_user_prompt, temperature=0.75, max_tokens=len(current_desc.split())*10 + 100) # Estimate token need

                if tailored_desc:
                    exp.description = tailored_desc
                    logger.info(f"Successfully tailored description for experience item {i+1}.")
                else:
                    logger.warning(f"Failed to tailor description for experience item {i+1} or LLM response was empty. Keeping original.")
                updated_experiences.append(exp) # Add the (potentially updated) experience back

            structured_data.experiences = updated_experiences # Replace with the list containing updated items
        else:
             logger.info("No experience entries found in structured data to tailor.")

    # Keep the generic error handling for the overall tailoring process
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM tailoring process: {e}", exc_info=True)

    # No need for specific openai errors here anymore as _call_llm handles them
    # except openai.APIError as e:
    #     logger.error(f"Azure OpenAI API returned an API Error: {e}")
    # except openai.APIConnectionError as e:
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