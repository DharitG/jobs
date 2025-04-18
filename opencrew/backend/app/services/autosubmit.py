import logging
from playwright.sync_api import sync_playwright, Playwright, Browser, Page, Error as PlaywrightError

from .. import models, schemas, crud # Potentially needed later
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
        job_url = application.job.url
        # resume_data = application.resume.content # Or parsed data if available
        # user_profile = {"full_name": user.full_name, "email": user.email, ...}

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
                page.goto(job_url, wait_until='domcontentloaded', timeout=30000) # 30s timeout
                logger.info(f"Successfully navigated to {job_url}")
                
                # --- TODO: Add Site-Specific Application Logic --- 
                # This is the complex part requiring site-specific selectors and actions.
                # Example structure:
                # if "greenhouse.io" in job_url:
                #     _fill_greenhouse_form(page, resume_data, user_profile)
                # elif "lever.co" in job_url:
                #     _fill_lever_form(page, resume_data, user_profile)
                # elif "indeed.com" in job_url: # Note: Indeed often uses iframes/complex flows
                #     _fill_indeed_form(page, resume_data, user_profile)
                # else:
                #     logger.warning(f"Unsupported job board/URL for auto-apply: {job_url}")
                #     # Update application status to indicate failure/manual required?
                #     return

                # --- Placeholder for successful submission logic --- 
                logger.info("Placeholder: Simulating form fill and submit.")
                page.wait_for_timeout(2000) # Simulate work
                
                # --- Update Application Status (Placeholder - Needs actual implementation) ---
                # IMPORTANT: Update status to APPLIED and set applied_at upon successful submission
                # This is crucial for the quota check to work correctly.
                try:
                    # Example:
                    application.status = models.ApplicationStatus.APPLIED # Assuming this enum exists
                    application.applied_at = datetime.utcnow()
                    db.add(application)
                    db.commit()
                    logger.info(f"Successfully applied and updated status for application {application_id}.")
                except Exception as update_e:
                    logger.error(f"Failed to update application status for {application_id} after simulated success: {update_e}")
                    db.rollback() # Rollback status update on error
                    # Consider re-raising or handling differently

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

def _fill_greenhouse_form(page: Page, resume_data: dict, user_profile: dict):
    logger.info("Attempting to fill Greenhouse form...")
    # TODO: Implement selectors and filling logic for Greenhouse
    raise NotImplementedError("Greenhouse form filling not implemented.")

def _fill_lever_form(page: Page, resume_data: dict, user_profile: dict):
    logger.info("Attempting to fill Lever form...")
    # TODO: Implement selectors and filling logic for Lever
    raise NotImplementedError("Lever form filling not implemented.")

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
