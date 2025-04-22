import logging
import re
from typing import List, Dict, Any, Optional # Added Optional

from ..schemas.resume import PdfTextItem, StructuredResume, BasicInfo, EducationItem, ExperienceItem, ProjectItem, SkillItem
import json # Added for LLM response parsing
from pydantic import ValidationError # Added for parsing validation

import openai # Added
from ..core.config import settings # Added


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


# --- LLM-Based Resume Parsing ---

def _parse_resume_with_llm(resume_text: str) -> StructuredResume:
    """
    Uses an LLM to parse raw resume text into the StructuredResume Pydantic model.
    """
    logger.info("Parsing resume text using LLM...")

    # Define the expected JSON structure based on Pydantic models
    # (Providing this in the prompt helps the LLM)
    schema_description = """
    The output MUST be a JSON object conforming to the following Pydantic schema structure:

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
        startDate: str | None = None # Format as YYYY-MM-DD or YYYY-MM or YYYY if possible
        endDate: str | None = None # Format as YYYY-MM-DD or YYYY-MM or YYYY or 'Present' if possible
        score: str | None = None # e.g., GPA
        courses: List[str] | None = None
        # highlights: List[str] | None = None # Exclude highlights for initial parsing

    class ExperienceItem(BaseModel):
        company: str
        position: str
        website: str | None = None
        startDate: str | None = None # Format as YYYY-MM-DD or YYYY-MM or YYYY if possible
        endDate: str | None = None # Format as YYYY-MM-DD or YYYY-MM or YYYY or 'Present' if possible
        summary: str | None = None # Overall summary of the role
        highlights: List[str] | None = None # Key responsibilities/achievements as bullet points

    class ProjectItem(BaseModel):
        name: str
        description: str | None = None
        keywords: List[str] | None = None
        url: str | None = None
        startDate: str | None = None # Format as YYYY-MM-DD or YYYY-MM or YYYY if possible
        endDate: str | None = None # Format as YYYY-MM-DD or YYYY-MM or YYYY if possible
        # highlights: List[str] | None = None # Exclude highlights for initial parsing

    class SkillItem(BaseModel):
        category: str # e.g., Programming Languages, Frameworks, Databases, Tools, Cloud Platforms
        skills: List[str]

    class StructuredResume(BaseModel):
        basic: BasicInfo | None = None
        objective: str | None = None # A concise career objective or summary statement
        education: List[EducationItem] | None = None
        experiences: List[ExperienceItem] | None = None
        projects: List[ProjectItem] | None = None
        skills: List[SkillItem] | None = None

    VERY IMPORTANT:
    - Output ONLY the JSON object. Do not include any introductory text, explanations, or markdown formatting like ```json ... ```.
    - Ensure the JSON is valid and strictly adheres to the specified Pydantic models.
    - Pay close attention to data types (string, list, etc.).
    - For dates (startDate, endDate), try to extract year, month, and day if available, otherwise use year-month or just year. Use 'Present' for ongoing roles/education. If dates are unclear, omit them (set to null/None).
    - For experience highlights, extract bullet points or descriptive sentences about responsibilities and achievements.
    - For skills, group related skills under appropriate categories (e.g., "Programming Languages", "Frameworks", "Databases", "Cloud Platforms", "Tools").
    """

    system_prompt = f"""You are an expert resume parser. Your task is to analyze the provided raw resume text and extract the information into a structured JSON format. {schema_description}"""
    user_prompt = f"""Parse the following resume text and generate the JSON output:

--- RESUME TEXT START ---
{resume_text}
--- RESUME TEXT END ---

JSON Output:"""

    # Use a potentially larger max_tokens for complex resumes
    max_parsing_tokens = 3000 # Adjust as needed based on typical resume complexity and model limits

    llm_response_str = _call_llm(system_prompt, user_prompt, temperature=0.2, max_tokens=max_parsing_tokens)

    if not llm_response_str:
        logger.error("LLM did not return a response for parsing.")
        # Return an empty structure or raise an error
        return StructuredResume(basic=BasicInfo(), objective="Failed to parse resume content via LLM.")

    try:
        # Clean potential markdown fences if the LLM ignored the instruction
        llm_response_str = llm_response_str.strip().removeprefix("```json").removesuffix("```").strip()
        # Parse the JSON string from the LLM response
        parsed_data = json.loads(llm_response_str)
        # Validate and structure the data using the Pydantic model
        structured_resume = StructuredResume(**parsed_data)
        logger.info("Successfully parsed resume text using LLM.")
        return structured_resume
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response from LLM: {e}")
        logger.debug(f"LLM Raw Response: {llm_response_str}")
        # Return an empty structure or raise an error
        return StructuredResume(basic=BasicInfo(), objective="Failed to parse LLM JSON response.")
    except ValidationError as e:
         logger.error(f"LLM JSON response failed Pydantic validation: {e}")
         logger.debug(f"LLM Raw Response: {llm_response_str}")
         # Return an empty structure or raise an error
         return StructuredResume(basic=BasicInfo(), objective="LLM response failed validation.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM response processing: {e}", exc_info=True)
        logger.debug(f"LLM Raw Response: {llm_response_str}")
        return StructuredResume(basic=BasicInfo(), objective="Unexpected error processing LLM response.")


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

    # 1. Concatenate text from PdfTextItems
    # Simple concatenation, preserving some spacing. Might need refinement.
    # Ensure items are roughly sorted by y then x coordinate if not already done by caller.
    # text_items.sort(key=lambda item: (item.y, item.x)) # Assuming y, x are available
    raw_resume_text = "\n".join(item.text for item in text_items) # Use 'text' field from PdfTextItem

    if not raw_resume_text.strip():
        logger.warning("No text content found in provided text items.")
        return StructuredResume(basic=BasicInfo(), objective="No text content found in resume.")

    # 2. Parse raw text into structured data using LLM
    structured_data = _parse_resume_with_llm(raw_resume_text)

    # 3. Tailor content using LLM (if job description is provided and parsing was successful)
    if job_description and structured_data and structured_data.objective != "Failed to parse resume content via LLM.": # Check if parsing succeeded
        structured_data = tailor_content(structured_data, job_description)
    elif not job_description:
        logger.info("No job description provided, skipping LLM tailoring.")

    logger.info("Resume processing and tailoring finished.")
    return structured_data