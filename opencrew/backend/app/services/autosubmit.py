import logging
import logging
from datetime import datetime # Import datetime
from playwright.sync_api import sync_playwright, Playwright, Browser, Page, Error as PlaywrightError
import time # For potential waits

from .. import models, schemas, crud
from ..db.session import SessionLocal # To get DB sessions if needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_browser(pw: Playwright) -> Browser:
    """Launches a Chromium browser instance."""
    # Consider adding options like headless=False for debugging
    # or proxy settings if needed.
    # Playwright downloads browsers on first run if not found.
    try:
        return pw.chromium.launch(headless=True)
    except Exception as e:
        logger.error(f"Failed to launch Playwright browser: {e}")
        logger.error("Ensure browser binaries are installed. Run 'playwright install' if needed.")
        raise

# --- Main Auto-Apply Function (Likely called by worker) ---
def apply_to_job(db: Session, application_id: int): # Added db parameter
    """
    Handles the auto-application process for a single job application record.
    Includes quota check before attempting automation.
    """
    logger.info(f"Starting auto-apply process for application ID: {application_id}")

    application: models.Application | None = None
    try:
        # --- Fetch Application Details ---
        # Use eager loading to get related objects in one query if performance becomes an issue
        application = db.query(models.Application).filter(models.Application.id == application_id).first()
        if not application:
            logger.error(f"Application not found for ID: {application_id}")
            return
        if not application.user:
             logger.error(f"User not found for application ID: {application_id}")
             return
        if not application.job:
             logger.error(f"Job not found for application ID: {application_id}")
             # Optionally update status to failed/error
             return
        if not application.resume:
             logger.error(f"Resume not found for application ID: {application_id}")
             # Optionally update status to failed/error
             return

        user = application.user
        job = application.job
        resume = application.resume
        job_url = job.url

        # --- Prepare Data ---
        # Assuming resume model has a file_path attribute pointing to the stored resume file
        if not resume.file_path:
             logger.error(f"Resume file path not found for resume ID: {resume.id}, application {application_id}")
             # Optionally update status to failed/error
             # crud.application.update_application(db, db_application=application, application_in={"status": models.ApplicationStatus.ERROR, "notes": "Resume file path missing"})
             # db.commit()
             return
        resume_data = {"file_path": resume.file_path} # Pass file path for upload

        # Basic user profile data (expand as needed based on form fields)
        user_profile = {
            "first_name": user.first_name or "", # Assuming these attributes exist on the User model
            "last_name": user.last_name or "",
            "email": user.email or "",
            "phone": user.phone_number or "", # Assuming phone_number attribute
            "linkedin_url": user.linkedin_url or "" # Assuming linkedin_url attribute
        }

        # --- Check Quota ---
        remaining_quota = check_user_quota(db=db, user=user)
        if remaining_quota <= 0:
            logger.warning(f"User {user.id} has no auto-apply quota remaining. Skipping application {application_id}.")
            # Optionally update application status to 'quota_exceeded' or similar
            # crud.application.update_application(db, db_application=application, application_in={"status": models.ApplicationStatus.ERROR, "notes": "Quota exceeded"})
            # db.commit() # Commit status update if done here
            return # Stop processing if quota exceeded

        logger.info(f"User {user.id} has {remaining_quota} auto-apply quota remaining. Proceeding with application {application_id}.")
        logger.info(f"Target job URL: {job_url}") # Log URL after quota check passes

        # --- Playwright Automation ---
        with sync_playwright() as pw:
            browser = _get_browser(pw)
            page = browser.new_page()
            logger.info(f"Navigating to {job_url}...")
            
            try:
                page.goto(job_url, wait_until='domcontentloaded', timeout=60000) # Increased timeout to 60s
                logger.info(f"Successfully navigated to {job_url}")

                # --- Site-Specific Application Logic ---
                applied_successfully = False
                if "greenhouse.io" in job_url:
                    applied_successfully = _fill_greenhouse_form(page, resume_data, user_profile)
                elif "lever.co" in job_url:
                    applied_successfully = _fill_lever_form(page, resume_data, user_profile)
                elif "indeed.com" in job_url:
                    # applied_successfully = _fill_indeed_form(page, resume_data, user_profile) # Call when implemented
                    logger.warning(f"Indeed auto-apply not yet implemented for {job_url}")
                else:
                    logger.warning(f"Unsupported job board/URL for auto-apply: {job_url}")

                # --- Update Application Status Based on Outcome ---
                if applied_successfully:
                    try:
                        application.status = models.ApplicationStatus.APPLIED # Assuming this enum exists
                        application.applied_at = datetime.utcnow()
                        db.add(application)
                        db.commit()
                        logger.info(f"Successfully applied and updated status for application {application_id}.")
                    except Exception as update_e:
                        logger.error(f"Failed to update application status for {application_id} after successful apply: {update_e}")
                        db.rollback() # Rollback status update on error
                else:
                    # Optionally update status to FAILED or keep as is if only unsupported
                    logger.info(f"Auto-apply did not complete successfully for application {application_id}.")
                    # Consider updating status to FAILED here if an attempt was made but failed
                    # crud.application.update_application(db, db_application=application, application_in={"status": models.ApplicationStatus.ERROR, "notes": "Auto-apply failed or unsupported"})
                    # db.commit()

            except PlaywrightError as e:
                logger.error(f"Playwright error during auto-apply for application {application_id} ({job_url}): {e}")
                # Optionally update status to failed/error
                # crud.application.update_application(db, db_application=application, application_in={"status": models.ApplicationStatus.ERROR, "notes": f"Playwright Error: {e}"})
                # db.commit()
            except Exception as e:
                logger.error(f"Unexpected error during auto-apply for application {application_id} ({job_url}): {e}")
                # Optionally update status to failed/error
                # crud.application.update_application(db, db_application=application, application_in={"status": models.ApplicationStatus.ERROR, "notes": f"Unexpected Error: {e}"})
                # db.commit()
            finally:
                logger.info("Closing browser page.")
                page.close()
                browser.close()

    except Exception as e:
        # Catch errors during Playwright startup/browser launch or DB fetch
        logger.error(f"Error during auto-apply setup or execution for application {application_id}: {e}")
        # Optionally update status to failed/error if application object exists
        # if application:
        #     try:
        #         crud.application.update_application(db, db_application=application, application_in={"status": models.ApplicationStatus.ERROR, "notes": f"Setup/Exec Error: {e}"})
        #         db.commit()
        #     except Exception as final_update_e:
        #         logger.error(f"Failed to update application {application_id} status to ERROR: {final_update_e}")
        #         db.rollback()

    # Final log message moved inside the try block's finally or after specific outcomes
    # logger.info(f"Finished auto-apply attempt for application ID: {application_id}")

# --- Helper functions for specific job boards (to be implemented) ---

def _fill_greenhouse_form(page: Page, resume_data: dict, user_profile: dict) -> bool:
    """Attempts to fill a standard Greenhouse application form. Returns True on success, False on failure."""
    logger.info("Attempting to fill Greenhouse form...")
    try:
        # --- Common Greenhouse Fields (Selectors are assumptions - VERIFY ON LIVE PAGES) ---
        logger.info("Filling basic info...")
        # Use specific IDs if available, otherwise rely on labels/names (less robust)
        page.locator('input[id*="first_name"]').fill(user_profile.get("first_name", ""))
        page.locator('input[id*="last_name"]').fill(user_profile.get("last_name", ""))
        page.locator('input[id*="email"]').fill(user_profile.get("email", ""))
        page.locator('input[id*="phone"]').fill(user_profile.get("phone", ""))

        # Resume Upload - Often has an input type="file" associated with a button/label
        # This selector looks for a button/label containing "Resume" and finds the associated file input
        logger.info(f"Uploading resume from: {resume_data.get('file_path')}")
        resume_input_selector = 'label:has-text("Resume") >> input[type="file"], button:has-text("Resume") >> input[type="file"], input[id*="resume"][type="file"]'
        page.locator(resume_input_selector).set_input_files(resume_data.get("file_path"))

        # LinkedIn URL (Optional field usually)
        linkedin_selector = 'input[name*="linkedin"]' # Common pattern
        if page.locator(linkedin_selector).is_visible():
             logger.info("Filling LinkedIn URL...")
             page.locator(linkedin_selector).fill(user_profile.get("linkedin_url", ""))

        # --- TODO: Handle Custom Questions ---
        # This is highly variable. Might need to loop through questions, identify types (text, dropdown, radio), and attempt to answer.
        # For now, just log a warning.
        logger.warning("Custom question handling not implemented for Greenhouse.")

        # --- TODO: Handle EEOC/Diversity Questions ---
        # These often appear at the end. Need strategies to select "Decline to self-identify" or similar.
        logger.warning("EEOC/Diversity question handling not implemented.")

        # --- Submission ---
        submit_button_selector = 'button[type="submit"]:has-text("Submit Application")'
        logger.info("Attempting to submit application...")
        page.locator(submit_button_selector).click() # Clicking submit

        # --- Verification Step ---
        # Wait for either a success message or a known failure indicator
        # Adjust selectors/text based on actual Greenhouse confirmation pages
        success_selector = 'text=/Application Submitted|Thank you/i' # Regex for common success text (case-insensitive)
        try:
             page.wait_for_selector(success_selector, timeout=15000) # Wait 15 seconds for confirmation
             logger.info("Greenhouse submission successful (confirmation text found).")
             return True
        except PlaywrightError:
             logger.warning("Greenhouse submission confirmation text not found within timeout.")
             # Add checks for known error messages if possible here
             return False

    except PlaywrightError as e:
        logger.error(f"Playwright error filling Greenhouse form: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error filling Greenhouse form: {e}")
        return False

def _fill_lever_form(page: Page, resume_data: dict, user_profile: dict) -> bool:
    """Attempts to fill a standard Lever application form. Returns True on success, False on failure."""
    logger.info("Attempting to fill Lever form...")
    try:
        # --- Common Lever Fields (Selectors are assumptions - VERIFY ON LIVE PAGES) ---
        logger.info("Filling basic info...")
        # Lever often uses name attributes like 'name', 'email', 'phone', 'urls[LinkedIn]'
        page.locator('input[name="name"]').fill(f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}")
        page.locator('input[name="email"]').fill(user_profile.get("email", ""))
        page.locator('input[name="phone"]').fill(user_profile.get("phone", ""))

        # Resume Upload - Look for input type="file" often named 'resume'
        logger.info(f"Uploading resume from: {resume_data.get('file_path')}")
        resume_input_selector = 'input[type="file"][name="resume"]'
        # Wait for the element to be visible and enabled before interacting
        page.locator(resume_input_selector).wait_for(state="visible", timeout=10000)
        page.locator(resume_input_selector).set_input_files(resume_data.get("file_path"))
        # Add a small wait after upload if needed for processing
        page.wait_for_timeout(1000)

        # LinkedIn URL
        linkedin_selector = 'input[name="urls[LinkedIn]"]'
        if page.locator(linkedin_selector).is_visible():
            logger.info("Filling LinkedIn URL...")
            page.locator(linkedin_selector).fill(user_profile.get("linkedin_url", ""))

        # --- TODO: Handle Custom Questions ---
        # Lever custom questions often appear within fieldsets or specific divs.
        logger.warning("Custom question handling not implemented for Lever.")

        # --- TODO: Handle EEOC/Diversity Questions ---
        # Similar to Greenhouse, often at the end.
        logger.warning("EEOC/Diversity question handling not implemented.")

        # --- Submission ---
        # Lever submit buttons often have text like "Submit Application" or similar
        submit_button_selector = 'button[type="submit"]' # May need refinement based on text like ':has-text("Submit Application")'
        logger.info("Attempting to submit application...")
        page.locator(submit_button_selector).click() # Clicking submit

        # --- Verification Step ---
        # Wait for either a success message or a known failure indicator
        # Adjust selectors/text based on actual Lever confirmation pages
        success_selector = 'text=/Application submitted|Your application has been received/i' # Regex for common success text
        try:
             page.wait_for_selector(success_selector, timeout=15000) # Wait 15 seconds for confirmation
             logger.info("Lever submission successful (confirmation text found).")
             return True
        except PlaywrightError:
             logger.warning("Lever submission confirmation text not found within timeout.")
             # Add checks for known error messages if possible here
             return False

    except PlaywrightError as e:
        logger.error(f"Playwright error filling Lever form: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error filling Lever form: {e}")
        return False

def _fill_indeed_form(page: Page, resume_data: dict, user_profile: dict):
    logger.info("Attempting to fill Indeed form...")
    # TODO: Implement selectors and filling logic for Indeed (likely complex)
    raise NotImplementedError("Indeed form filling not implemented.")

# Example usage (for testing, likely called by a worker task)
if __name__ == "__main__":
    test_application_id = 1
    apply_to_job(test_application_id)

# Placeholder for the main auto-submission logic
def submit_application(
    db_session, # Need a way to pass DB session to background tasks
    user_id: int, 
    job_id: int, 
    resume_id: int
):
    logger.info(f"Placeholder: Auto-submitting application for user {user_id} to job {job_id} using resume {resume_id}")
    
    # 1. Fetch user, job, resume details from DB using crud functions
    user = crud.user.get_user(db_session, user_id=user_id)
    job = crud.job.get_job(db_session, job_id=job_id)
    resume = crud.resume.get_resume(db_session, resume_id=resume_id)
    
    if not all([user, job, resume]):
        logger.error("Could not find user, job, or resume for auto-submit.")
        return False

    # 2. Check user's quota/subscription tier
    # quota_remaining = check_user_quota(user)
    # if quota_remaining <= 0:
    #     logger.warning(f'User {user_id} has no auto-apply quota left.')
    #     return False

    # 3. Launch browser automation (e.g., Playwright)
    # try:
    #     with sync_playwright() as p:
    #         browser = p.chromium.launch()
    #         page = browser.new_page()
    #         page.goto(job.url)
    #         # ... Logic to navigate ATS, fill forms using resume/user data ...
    #         logger.info(f'Successfully submitted application for job: {job.title}')
    #         browser.close()
    #         # Decrement quota
    #         # update_application_status(db_session, application_id, status='submitted')
    #         return True
    # except Exception as e:
    #     logger.error(f'Error during auto-submit for job {job.id}: {e}')
    #     # update_application_status(db_session, application_id, status='failed')
    #     return False

    logger.warning("Browser automation logic is not implemented.")
    return False # Placeholder return

# --- Quota Checking Logic ---

# Define quota limits per tier
QUOTA_LIMITS = {
    models.SubscriptionTier.FREE: 50,
    models.SubscriptionTier.PRO: 10000,  # Effectively unlimited
    models.SubscriptionTier.ELITE: 10000, # Effectively unlimited
}

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime

def check_user_quota(db: Session, user: models.User) -> int:
    """
    Checks the remaining auto-apply quota for the user in the current calendar month.
    Returns the number of applications remaining.
    """
    limit = QUOTA_LIMITS.get(user.subscription_tier, 0)
    if limit >= 10000: # Treat high limits as unlimited
        logger.info(f"User {user.id} has '{user.subscription_tier}' tier (unlimited quota).")
        return limit # Return a large number indicating unlimited

    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    try:
        # Count applications successfully submitted via auto-apply this month
        # Assuming 'APPLIED' status and a non-null 'applied_at' indicates a successful auto-apply
        # Adjust status check if needed based on actual application flow
        applied_count = db.query(func.count(models.Application.id))\
            .filter(
                models.Application.user_id == user.id,
                models.Application.status == models.ApplicationStatus.APPLIED, # Check for success status
                models.Application.applied_at >= start_of_month
            ).scalar() or 0 # scalar() returns None if count is 0

        remaining = limit - applied_count
        logger.info(f"User {user.id} (Tier: {user.subscription_tier}): Limit={limit}, Used={applied_count}, Remaining={max(0, remaining)}")
        return max(0, remaining) # Ensure non-negative return

    except Exception as e:
        logger.error(f"Error checking quota for user {user.id}: {e}")
        return 0 # Fail safe: assume no quota left if error occurs
