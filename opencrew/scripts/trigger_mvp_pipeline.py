import argparse
import logging
import asyncio
from sqlalchemy.orm import Session

# Need to adjust imports based on actual project structure and where DB session/services are accessible
# This assumes the script is run from the 'backend' directory or the Python path is set correctly.
from app.db.session import SessionLocal
from app import crud, schemas
from app.services import matching
from app.services import autosubmit
from app.core.config import settings # For potential settings needed by services

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_mvp_pipeline(db: Session, user_id: int):
    """
    Manually triggers the matching and auto-apply pipeline for MVP demonstration.
    """
    logger.info(f"Starting MVP pipeline trigger for user_id: {user_id}")

    # 1. Get User
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found.")
        return
    logger.info(f"Found user: {user.email}")

    # 2. Get User's latest resume with structured_data
    # Assuming the latest resume is the one we want to use
    resumes = crud.resume.get_resumes_by_owner(db, owner_id=user_id, limit=1, skip=0) # Get the most recent one
    if not resumes:
        logger.error(f"No resumes found for user {user_id}.")
        return

    latest_resume = resumes[0]
    if not latest_resume.structured_data:
        logger.error(f"Resume ID {latest_resume.id} for user {user_id} does not have structured_data. Run /parse-and-tailor first.")
        # Attempt to load as StructuredResume schema for validation/use
        try:
            structured_resume_data = schemas.StructuredResume(**latest_resume.structured_data)
            logger.info(f"Loaded structured data for resume ID: {latest_resume.id}")
        except Exception as e:
             logger.error(f"Failed to parse structured_data for resume ID {latest_resume.id}: {e}")
             return
    else:
         logger.error(f"Resume ID {latest_resume.id} for user {user_id} does not have structured_data. Run /parse-and-tailor first.")
         return


    # 3. Get a few sample jobs from the DB
    jobs = crud.job.get_jobs(db, skip=0, limit=5) # Get 5 jobs for testing
    if not jobs:
        logger.error("No jobs found in the database to match against.")
        return
    logger.info(f"Found {len(jobs)} jobs to match against.")

    # 4. Run the matching service
    # Assuming matching service takes structured resume and list of jobs
    # Adjust function call signature as needed
    logger.info("Running matching service...")
    try:
        # The matching service might need adjustment to accept StructuredResume directly
        # or we might need to adapt the input here based on its expectations.
        matched_job_ids = matching.find_matching_jobs(
            resume_data=structured_resume_data, # Pass the parsed structured data
            user_preferences={}, # Add user preferences if applicable
            jobs_to_match=jobs,
            threshold=settings.MATCHING_THRESHOLD # Example threshold
        )
        logger.info(f"Matching complete. Found {len(matched_job_ids)} potential matches: {matched_job_ids}")
        if not matched_job_ids:
            logger.info("No matches found for this resume and job set.")
            return
    except Exception as e:
        logger.error(f"Error during matching service execution: {e}", exc_info=True)
        return


    # 5. Trigger auto-apply for matched jobs
    # Assuming autosubmit service takes user and list of matched job IDs
    logger.info(f"Attempting auto-apply for matched jobs: {matched_job_ids}")
    matched_jobs = [job for job in jobs if job.id in matched_job_ids] # Get the full job objects

    try:
        # Assuming autosubmit.submit_applications is an async function
        # Pass the structured resume data for filling forms
        await autosubmit.submit_applications(
            db=db,
            user=user,
            jobs=matched_jobs,
            structured_resume=structured_resume_data
        )
        logger.info("Auto-apply process initiated (check service logs/DB for individual job statuses).")
        logger.warning("Note: Actual success depends on CAPTCHA handling and adapter robustness (currently limited).")
    except Exception as e:
         logger.error(f"Error during auto-submit service execution: {e}", exc_info=True)


    logger.info(f"MVP pipeline trigger finished for user_id: {user_id}")


async def main():
    parser = argparse.ArgumentParser(description="Trigger MVP Matching and Auto-Apply Pipeline")
    parser.add_argument("user_id", type=int, help="ID of the user to run the pipeline for")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        await run_mvp_pipeline(db, args.user_id)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())