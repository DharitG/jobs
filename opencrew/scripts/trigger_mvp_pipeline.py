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


    # 5. Find or Create Application records and trigger auto-apply tasks
    logger.info(f"Processing auto-apply for matched job IDs: {matched_job_ids}")
    application_tasks = []
    for job_id in matched_job_ids:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            logger.warning(f"Job ID {job_id} from matches not found in DB. Skipping.")
            continue

        # Find existing application or create a new one
        application = db.query(models.Application).filter(
            models.Application.user_id == user_id,
            models.Application.job_id == job_id
        ).first()

        if application:
            logger.info(f"Found existing application ID: {application.id} for user {user_id} and job {job_id}")
            # Optionally: Check status before re-triggering?
            # if application.status == models.ApplicationStatus.APPLIED:
            #     logger.info(f"Application {application.id} already applied. Skipping.")
            #     continue
            application.status = models.ApplicationStatus.PENDING # Reset status for re-try
            application.notes = "Pipeline triggered again."
            application.resume_id = latest_resume.id # Ensure latest resume is linked
        else:
            logger.info(f"Creating new application record for user {user_id} and job {job_id}")
            application_create = schemas.ApplicationCreate(
                status=models.ApplicationStatus.PENDING,
                notes="Created by MVP pipeline trigger.",
                job_id=job_id,
                resume_id=latest_resume.id # Link the latest resume
            )
            application = crud.application.create_user_application(
                db=db, application=application_create, user_id=user_id
            )
            db.flush() # Ensure ID is generated if needed immediately
            logger.info(f"Created new application ID: {application.id}")

        if application:
             # Add the async task call to a list
            application_tasks.append(autosubmit.apply_to_job_async(db=db, application_id=application.id))
        else:
             logger.error(f"Failed to find or create application for job {job_id}. Cannot trigger auto-apply.")

    # Execute all application tasks concurrently
    if application_tasks:
        logger.info(f"Running {len(application_tasks)} auto-apply tasks concurrently...")
        results = await asyncio.gather(*application_tasks, return_exceptions=True)
        logger.info("Finished running auto-apply tasks.")
        # Log results/exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # The exception is already logged within apply_to_job_async's final catch block
                logger.error(f"Task for application (index {i}) failed with an exception: {result}")
            # else: # Success is logged within apply_to_job_async
            #    logger.info(f"Task for application (index {i}) completed.")
    else:
        logger.info("No application tasks to run.")


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