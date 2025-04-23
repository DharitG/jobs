import logging
import asyncio
import time
import json # Import json
from pathlib import Path # Import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type
from urllib.parse import urlparse

# from playwright.async_api import async_playwright, Browser, Page, Locator, Error as PlaywrightError # Likely managed by browser-use
# from playwright_stealth import stealth_async # Likely managed by browser-use
# from sentence_transformers import SentenceTransformer, util # Replaced by LLM's understanding
# import torch # Sentence Transformers dependency

# --- New Imports ---
import os
from dotenv import load_dotenv
from browser_use import Agent # The core agent from browser-use
from langchain_openai import ChatOpenAI # Example LLM integration
from pydantic import ValidationError # For loading structured data

# Import the new PDF generator service and schema
from .pdf_generator import StructuredResumePdfGenerator
from ..schemas.resume import StructuredResume

load_dotenv() # Load .env file for API keys
# --- End New Imports ---
# Telemetry Imports (Placeholders - require installation and configuration)
# from prometheus_client import Counter, Gauge # Example
# from opentelemetry import trace # Example
# from opentelemetry.trace.status import Status, StatusCode # Example

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import schemas, crud # Absolute imports
from app.models.application import Application, ApplicationStatus # Import specific models/enums
from app.models.user import User, SubscriptionTier # Import specific models/enums
from app.models.job import Job # Import specific models/enums
from app.models.resume import Resume # Import specific models/enums
from app.db.session import SessionLocal # To get DB sessions if needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Artifact Handling ---
import tempfile
import shutil # Keep for potential temp file cleanup if needed
import boto3 # Import AWS SDK
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError # Import specific exceptions
from app.core.config import settings # Absolute import

# ARTIFACT_DIR = Path(tempfile.gettempdir()) / "opencrew_artifacts" # No longer saving locally by default
# ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def upload_screenshot_to_s3(history, application_id: int, outcome: str) -> Optional[str]:
    """Uploads the last screenshot from AgentHistoryList to S3 and returns the URL."""
    try:
        screenshot_paths = history.screenshots() # Get list of screenshot paths
        if not screenshot_paths:
            logger.info(f"No screenshots found in history for app {application_id}.")
            return None

        last_screenshot_source_path_str = screenshot_paths[-1]
        last_screenshot_source_path = Path(last_screenshot_source_path_str) # Keep as Path for existence check

        if not last_screenshot_source_path.exists():
            logger.warning(f"Source screenshot path '{last_screenshot_source_path_str}' not found for app {application_id}.")
            return None

        # --- S3 Upload Logic ---
        if not settings.S3_BUCKET_NAME or not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            logger.error(f"S3 credentials or bucket name not configured. Cannot upload screenshot for app {application_id}.")
            return None

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Define a key (path within the bucket)
        s3_key = f"application_screenshots/app_{application_id}_{outcome}_{timestamp}.png"

        try:
            logger.info(f"Uploading screenshot for app {application_id} from '{last_screenshot_source_path_str}' to s3://{settings.S3_BUCKET_NAME}/{s3_key}")
            s3_client.upload_file(
                Filename=last_screenshot_source_path_str,
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                ExtraArgs={'ContentType': 'image/png'} # Ensure correct content type
            )

            # Construct the object URL (basic version, consider using get_object_url or presigned URLs if needed)
            # Note: Assumes bucket has public read access or uses other auth mechanisms (e.g., CloudFront)
            # For private buckets, you'd generate a presigned URL here instead.
            s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{s3_key}"
            logger.info(f"Successfully uploaded screenshot for app {application_id} to S3: {s3_url}")
            return s3_url

        except (NoCredentialsError, PartialCredentialsError):
            logger.error(f"AWS credentials not found or incomplete for S3 upload (app {application_id}).")
        except ClientError as e:
            # More specific error handling for S3 issues (e.g., bucket not found, permissions)
            logger.error(f"S3 ClientError during upload for app {application_id}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload for app {application_id}: {e}", exc_info=True)

        return None # Return None if upload fails

    except Exception as e:
        logger.error(f"Error processing screenshot history for app {application_id}: {e}", exc_info=True)
        return None

# --- Telemetry Placeholders ---
# tracer = trace.get_tracer(__name__) # Example OTel tracer
# AUTOSUBMIT_SUCCESS_COUNTER = Counter('autosubmit_success_total', 'Total successful auto-submissions') # Example Prometheus Counter
# AUTOSUBMIT_FAILURE_COUNTER = Counter('autosubmit_failure_total', 'Total failed auto-submissions', ['adapter', 'state']) # Example Prometheus Counter with labels
# ACTIVE_AUTOSUBMIT_GAUGE = Gauge('autosubmit_active_tasks', 'Number of auto-submit tasks currently running') # Example Prometheus Gauge


# --- Data Structures (Commented out - New approach might have different output) ---
# @dataclass
# class TaskResult:
#     """Holds the outcome and artifacts of an auto-apply task."""
#     success: bool = False
#     message: str = ""
#     state: str = "START" # Last successful state (e.g., LOGIN, FORM_FILL, VERIFY)
#     html: Optional[str] = None
#     screenshot: Optional[bytes] = None
#     har: Optional[Dict] = None # Playwright HAR data
#     error: Optional[str] = None

# @dataclass
# class JobApplicationTask: # Keep this for now, useful for input structure
#     """Input data for the AutoSubmitter."""
#     application_id: int
#     job_url: str
#     resume_path: str
#     profile: Dict[str, Any] # User profile data (first_name, email, etc.)
#     credentials: Dict[str, str] = field(default_factory=dict) # Site-specific login credentials (if needed/stored)

# --- CAPTCHA Handling (Commented out - Needs different integration) ---
# class CaptchaGate: ... (Full class commented out)

# --- Selector Loading (Commented out - Replaced by Agent) ---
# SELECTOR_DIR = Path(__file__).parent / "ats_selectors"
# def load_selectors(adapter_name: str) -> Dict[str, str]: ... (Full function commented out)

# --- Semantic Fallback Helper (Commented out - Replaced by Agent) ---
# try: ... (Full try-except block commented out)
# semantic_model = None
# async def find_element_by_semantic_label(page: Page, target_label: str, element_type: str = "input") -> Optional[Locator]: ... (Full function commented out)


# --- Adapters (Commented out - Replaced by Agent) ---
# class BaseAdapter: ... (Full class commented out)
# class GreenhouseAdapter(BaseAdapter): ... (Full class commented out)
# class LeverAdapter(BaseAdapter): ... (Full class commented out)
# class IndeedAdapter(BaseAdapter): ... (Full class commented out)
# class WorkdayAdapter(BaseAdapter): ... (Full class commented out)

# --- Site Detection (Commented out - Replaced by Agent) ---
# def detect_site(url: str) -> Optional[Type[BaseAdapter]]: ... (Full function commented out)

# --- AutoSubmitter Class (State Machine) (Commented out - Replaced by Agent) ---
# class AutoSubmitter: ... (Full class commented out)


# --- Main Entry Point (Refactored for browser-use) ---

async def apply_to_job_async(db: Session, application_id: int):
    """
    Async function to handle the auto-application process for a single job application record.
    """
    logger.info(f"Starting async auto-apply process for application ID: {application_id}")
    application: Application | None = None # Use imported Application type
    original_temp_resume_path = None # Path for the original downloaded resume
    tailored_resume_path = None # Path for the newly generated tailored PDF

    try:
        # --- Fetch Application Details ---
        application = db.query(Application).filter(Application.id == application_id).first() # Use imported Application type
        if not application:
            logger.error(f"Application not found for ID: {application_id}")
            return
        if not application.user or not application.job or not application.resume:
            logger.error(f"Missing user, job, or resume for application ID: {application_id}")
            # Update status to error in DB
            application.status = ApplicationStatus.ERROR # Use imported Enum
            application.notes = "Missing required data (user, job, or resume)."
            db.add(application)
            db.commit()
            return
        # Check for original_filepath (where S3 key is stored) instead of file_path
        if not application.resume.original_filepath:
            logger.error(f"Resume original_filepath (S3 key) not found for resume ID: {application.resume.id}, application {application_id}")
            application.status = ApplicationStatus.ERROR # Use imported Enum
            application.notes = "Resume S3 key missing."
            db.add(application)
            db.commit()
            return

        user = application.user
        job = application.job
        resume = application.resume

        # --- Check Quota ---
        remaining_quota = check_user_quota(db=db, user=user)
        if remaining_quota <= 0:
            logger.warning(f"User {user.id} has no auto-apply quota remaining. Skipping application {application_id}.")
            application.status = ApplicationStatus.ERROR # Use imported Enum (Or a specific 'QUOTA_EXCEEDED' status)
            application.notes = "Auto-apply quota exceeded for the month."
            db.add(application)
            db.commit()
            return

        logger.info(f"User {user.id} has {remaining_quota} auto-apply quota remaining. Proceeding with application {application_id}.")

        # --- Elite Tier Throttling (Placeholder) ---
        if user.subscription_tier == SubscriptionTier.ELITE: # Use imported Enum
            # TODO: Implement actual throttling logic (e.g., check last N application timestamps)
            throttle_delay_seconds = 5.0 + (time.time() % 5) # Example: Wait 5-10 seconds
            logger.info(f"Elite tier user {user.id}. Applying placeholder throttle delay of {throttle_delay_seconds:.1f} seconds.")
            await asyncio.sleep(throttle_delay_seconds)

        # --- Prepare Task Data ---
        user_profile = {
            "first_name": user.first_name or "", # Use new field
            "last_name": user.last_name or "",   # Use new field
            "email": user.email or "",
            "phone": user.phone_number or "", # Use new field
            "linkedin_url": user.linkedin_url or "" # Use new field
        }
        # Ensure resume.original_filepath (S3 key) is available.
        resume_s3_key = resume.original_filepath
        if not resume_s3_key:
             # This case should have been caught earlier, but double-check
             logger.error(f"Critical: Resume S3 key missing before execution for app {application_id}.")
             application.status = ApplicationStatus.ERROR # Use imported Enum
             application.notes = "Critical: Resume S3 key missing just before execution."
             db.add(application)
             db.commit()
             return

        # --- Download Original Resume from S3 to Temporary File ---
        # Check S3 configuration first
        if not settings.S3_BUCKET_NAME or not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
             logger.error(f"S3 credentials or bucket name not configured. Cannot download resume for app {application_id}.")
             raise ValueError("S3 storage not configured for resume download.") # Raise error to stop processing

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )
        # Create a temporary file with the correct extension (e.g., .pdf)
        file_suffix = Path(resume_s3_key).suffix or '.pdf' # Get suffix from key or default
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
            original_temp_resume_path = temp_file.name # Store the path of the original download
            logger.info(f"Downloading original resume from s3://{settings.S3_BUCKET_NAME}/{resume_s3_key} to {original_temp_resume_path} for app {application_id}")
            s3_client.download_file(settings.S3_BUCKET_NAME, resume_s3_key, original_temp_resume_path)
            logger.info(f"Successfully downloaded original resume to {original_temp_resume_path}")
        # --- End Download ---

        # --- Generate Tailored PDF if Structured Data Exists ---
        resume_to_use_path = original_temp_resume_path # Default to original S3 resume
        if resume.structured_data:
            logger.info(f"Structured data found for resume ID {resume.id}. Attempting to generate tailored PDF.")
            try:
                # Load structured data into Pydantic model
                structured_resume = StructuredResume(**resume.structured_data)

                # Instantiate generator and generate PDF
                pdf_generator = StructuredResumePdfGenerator()
                temp_pdf_dir = tempfile.gettempdir() # Use system temp dir
                tailored_resume_path = pdf_generator.generate_resume_pdf(structured_resume, temp_pdf_dir)
                logger.info(f"Successfully generated tailored PDF: {tailored_resume_path}")
                resume_to_use_path = tailored_resume_path # Use the tailored PDF path for the agent

            except ValidationError as ve:
                logger.error(f"Pydantic validation error loading structured_data for resume {resume.id}: {ve}. Using original resume.", exc_info=True)
                tailored_resume_path = None # Ensure path is None if generation fails
            except Exception as pdf_gen_error:
                logger.error(f"Failed to generate tailored PDF for resume {resume.id}: {pdf_gen_error}. Using original resume.", exc_info=True)
                tailored_resume_path = None # Ensure path is None if generation fails
        else:
            logger.info(f"No structured data found for resume ID {resume.id}. Using original resume from S3.")
        # --- End PDF Generation ---


        # --- Execute browser-use Agent ---
        agent_success = False
        agent_message = "Agent execution started."
        agent_error_details = None # Changed from agent_error to avoid shadowing

        # Define the task for the AI agent
        profile_str = "\n".join([f"- {k}: {v}" for k, v in user_profile.items() if v])
        task_prompt = f"""
        Objective: Apply for the job at the following URL: {job.url}

        Applicant Profile:
        {profile_str}

        Resume File Path: {resume_to_use_path} # Use the path to the resume file (original or tailored)

        Instructions:
        1. Navigate to the job URL: {job.url}
        2. Fill out the application form using the provided applicant profile information.
        3. **Important:** Handle resume upload. The resume file is located at the local path: **{resume_to_use_path}**. Use this path when interacting with the file upload element on the job site.
        4. Handle any standard questions (like work authorization, sponsorships) appropriately based on typical US-based applicant information unless specified otherwise in the profile. You may need to select "Yes" for authorization and "No" for sponsorship if unsure and fields are required.
        5. Answer basic EEOC questions (Gender, Race, Ethnicity, Veteran Status, Disability) by selecting "Decline to self-identify" or similar options if available and required.
        6. Do NOT attempt to answer complex custom questions requiring free-text input (e.g., "Why do you want to work here?", salary expectations) unless the answer is directly in the profile. Skip them if possible, otherwise stop and report the blockage.
        7. Submit the application.
        8. Verify if the submission was successful (look for confirmation messages). If errors occur, report them.

        Provide a final status message indicating success or failure, and mention any fields you couldn't fill or steps you couldn't complete.
        """

        # Configure the LLM (ensure OPENAI_API_KEY is set in .env)
        llm = ChatOpenAI(model="gpt-4o", temperature=0.2) # Using GPT-4o as example

        # Instantiate and run the agent
        logger.info(f"Instantiating browser-use Agent for application {application_id}")
        agent = Agent(
            task=task_prompt,
            llm=llm,
            # Add browser_args, viewport, etc. if needed for stealth/config
            # browser_args=["--no-sandbox"], # Example for Linux environments
            # viewport={"width": 1920, "height": 1080}
        )

        history = await agent.run() # agent.run() returns AgentHistoryList
        logger.info(f"Agent execution finished for application {application_id}.")
        # logger.debug(f"Agent history details: {history}") # Optional: Log full history for debugging

        # --- Interpret Agent Result using AgentHistoryList ---
        final_screenshot_url = None # Initialize outside try block

        try:
            if history and history.is_done() and not history.has_errors():
                agent_success = True
                agent_message = history.final_result() or "Application submitted successfully by agent."
                logger.info(f"Agent task marked as done without errors for application {application_id}. Final result: {agent_message}")
                # Upload final screenshot on success
                final_screenshot_url = upload_screenshot_to_s3(history, application_id, "success")

            elif history:
                # Agent finished but didn't mark as done, or encountered errors
                agent_success = False
                errors = history.errors()
                final_output = history.final_result()
                if errors:
                    agent_error_details = "; ".join(map(str, errors)) # Combine multiple errors if they exist
                    agent_message = f"Agent encountered errors: {agent_error_details}"
                    if final_output:
                        agent_message += f" | Final agent output: {final_output}"
                    logger.warning(f"Agent task had errors for application {application_id}: {agent_error_details}")
                elif not history.is_done():
                    agent_message = f"Agent did not complete the task. Final output: {final_output}"
                    logger.warning(f"Agent task not marked as done for application {application_id}. Final output: {final_output}")
                else: # Should ideally not happen if has_errors() is reliable
                    agent_message = f"Agent finished with unclear status (done: {history.is_done()}, errors: {history.has_errors()}). Final output: {final_output}"
                    logger.warning(agent_message)
                # Upload final screenshot on failure/error
                final_screenshot_url = upload_screenshot_to_s3(history, application_id, "failure")

            else:
                # Should not happen if agent.run() always returns history, but handle defensively
                agent_success = False
                agent_message = "Agent execution finished but no history object was returned."
                logger.error(agent_message)

        except Exception as history_parse_error:
             logger.error(f"Error parsing agent history for application {application_id}: {history_parse_error}", exc_info=True)
             agent_success = False
             agent_message = f"Failed to interpret agent result: {history_parse_error}"
             agent_error_details = str(history_parse_error)


    except Exception as agent_exec_error:
        # Catch errors during the agent instantiation or run() call itself, or PDF generation/download
        logger.error(f"Error during auto-apply setup or execution for application {application_id}: {agent_exec_error}", exc_info=True)
        agent_success = False
        agent_message = f"Auto-apply setup or agent execution failed: {agent_exec_error}"
        agent_error_details = str(agent_exec_error)
        # Attempt to save screenshot even if agent execution failed mid-way, if history exists (unlikely here)
        # if 'history' in locals() and history:
        #      final_screenshot_url = upload_screenshot_to_s3(history, application_id, "failure_exec")


    finally:
        # --- Clean up temporary resume files ---
        # Delete original downloaded resume
        if original_temp_resume_path and Path(original_temp_resume_path).exists():
            try:
                Path(original_temp_resume_path).unlink()
                logger.info(f"Successfully deleted temporary original resume file: {original_temp_resume_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to delete temporary original resume file {original_temp_resume_path}: {cleanup_error}")
        # Delete tailored generated resume if it exists
        if tailored_resume_path and Path(tailored_resume_path).exists():
            try:
                Path(tailored_resume_path).unlink()
                logger.info(f"Successfully deleted temporary tailored resume file: {tailored_resume_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to delete temporary tailored resume file {tailored_resume_path}: {cleanup_error}")

    # --- Update Application Status (Moved outside main try block to ensure it runs even if agent init fails) ---
    # Ensure application object is available
    if not application:
         logger.error(f"Application object is None, cannot update status for application ID {application_id}")
         # Attempt to fetch again or handle error appropriately
         # This case should ideally be prevented by earlier checks, but handle defensively.
         try:
             db.rollback() # Rollback any potential uncommitted changes from failed setup
         except Exception as rb_err:
              logger.error(f"Rollback failed after application object became None for ID {application_id}: {rb_err}")
         return # Cannot proceed without application object

    if agent_success:
        application.status = ApplicationStatus.APPLIED # Use imported Enum
        application.applied_at = datetime.utcnow()
        application.notes = agent_message # Use message derived from history
    else:
        application.status = ApplicationStatus.ERROR # Use imported Enum (Or a more specific failure status)
        # Combine message and error details for notes
        application.notes = f"Auto-apply failed. Reason: {agent_message}" # Updated message prefix
        if agent_error_details:
            application.notes += f" | Details: {agent_error_details}" # Updated label

    # Save the S3 URL to the database (if generated)
    if 'final_screenshot_url' in locals() and final_screenshot_url:
        application.screenshot_url = final_screenshot_url
    else:
         application.screenshot_url = None # Ensure it's null if upload failed or wasn't attempted

    try:
        db.add(application)
        db.commit()
        logger.info(f"Finished auto-apply attempt for application ID: {application_id}. Agent Success: {agent_success}. Final Status: {application.status}. Final Notes: {application.notes}")
    except Exception as final_commit_e:
         logger.error(f"Failed to commit final application status update for ID {application_id}: {final_commit_e}", exc_info=True)
         db.rollback()


# --- Quota Checking Logic (Unchanged) ---
QUOTA_LIMITS = {
    SubscriptionTier.FREE: 50, # Use imported Enum
    SubscriptionTier.PRO: 10000,  # Effectively unlimited
    SubscriptionTier.ELITE: 10000, # Effectively unlimited
}

def check_user_quota(db: Session, user: User) -> int: # Use imported User type
    """
    Checks the remaining auto-apply quota for the user in the current calendar month.
    Returns the number of applications remaining.
    """
    limit = QUOTA_LIMITS.get(user.subscription_tier, 0)
    # Check for Pro or Elite tiers specifically for unlimited quota
    if user.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ELITE]: # Use imported Enum
        logger.info(f"User {user.id} has '{user.subscription_tier}' tier. Granting unlimited auto-apply quota.")
        return 99999 # Return a very large number to signify unlimited

    # For FREE tier or any other tiers without explicit unlimited quota
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    try:
        applied_count = db.query(func.count(Application.id)) \
            .filter(
                Application.user_id == user.id,
                Application.status == ApplicationStatus.APPLIED,
                Application.applied_at >= start_of_month
            ).scalar() or 0

        remaining = limit - applied_count
        logger.info(f"User {user.id} (Tier: {user.subscription_tier}): Monthly Limit={limit}, Used This Month={applied_count}, Remaining={max(0, remaining)}")
        return max(0, remaining) # Ensure non-negative return

    except Exception as e:
        logger.error(f"Error checking quota for user {user.id}: {e}")
        return 0
