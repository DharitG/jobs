import logging
import asyncio # Import asyncio
from typing import List

from .celery_app import celery_app # Import the configured Celery app
from ..services import autosubmit, scraping, matching # Import scraping and matching services
from ..db.session import SessionLocal # Needed for DB operations within tasks
from .. import crud, schemas # Needed for DB operations

logger = logging.getLogger(__name__)

@celery_app.task(acks_late=True, name="tasks.trigger_auto_apply") # Use explicit name
def trigger_auto_apply(application_id: int):
    """Celery task to trigger the auto-application process for a given application ID."""
    logger.info(f"Received task trigger_auto_apply for application_id: {application_id}")
    db = SessionLocal()
    try:
        # Call the new async auto-submit function using asyncio.run()
        asyncio.run(autosubmit.apply_to_job_async(db=db, application_id=application_id))
        # Logging and status updates are now handled within apply_to_job_async
        logger.info(f"Finished processing task trigger_auto_apply for application_id: {application_id}")
    except Exception as e:
        # Log the error; Celery can handle retries based on configuration if needed
        # Rollback might be redundant if apply_to_job_async handles its own errors/rollbacks,
        # but keep it here as a safety net for unexpected exceptions before/after the async call.
        try:
            db.rollback()
        except Exception as rb_exc:
            logger.error(f"Error during rollback attempt for application_id {application_id}: {rb_exc}")

        logger.error(f"Error processing task trigger_auto_apply for application_id: {application_id}. Error: {e}", exc_info=True)
        # Depending on retry policy, this might raise the exception to trigger a retry
        raise
    finally:
        db.close() # Ensure the session is always closed

# Add other tasks here later, e.g.:
# @celery_app.task(name="tasks.send_email")
# def send_email_task(recipient: str, subject: str, body: str):
#     from ..services import emailer # Import here to avoid circular dependencies
#     emailer.send_email(to=recipient, subject=subject, body=body)


@celery_app.task(acks_late=True, name="tasks.run_all_scrapers")
def run_all_scrapers_task():
    """Celery task to run all configured job scrapers."""
    logger.info("Starting task: run_all_scrapers_task")
    try:
        scraped_jobs: List[schemas.JobCreate] = scraping.run_scrapers()
        logger.info(f"Scraping completed. Found {len(scraped_jobs)} jobs.")

        # --- Integrate Job Processing/Indexing ---
        db = SessionLocal()
        new_jobs_count = 0
        indexed_jobs_count = 0
        try:
            for job_data in scraped_jobs:
                # Ensure URL is a string for DB lookup
                job_url_str = str(job_data.url)
                existing_job = crud.job.get_job_by_url(db, url=job_url_str)
                if not existing_job:
                    try:
                        # create_job handles embedding generation internally if description exists
                        created_job = crud.job.create_job(db, job=job_data)
                        new_jobs_count += 1
                        logger.info(f"Created new job in DB: ID {created_job.id}, Title: {created_job.title}")

                        # Index in Qdrant if embedding was generated
                        if created_job.embedding:
                            # index_job expects the embedding list directly
                            if matching.index_job(job=created_job, job_embedding=created_job.embedding):
                                indexed_jobs_count += 1
                            else:
                                logger.warning(f"Failed to index job ID {created_job.id} in Qdrant.")
                        else:
                            logger.info(f"Skipping Qdrant indexing for job ID {created_job.id} (no embedding).")

                    except Exception as create_exc:
                        logger.error(f"Failed to create or index job with URL {job_url_str}: {create_exc}", exc_info=True)
                        db.rollback() # Rollback the specific failed job creation
                # else: # Optional: Log if job already exists
                #     logger.debug(f"Job with URL {job_url_str} already exists. Skipping.")

            logger.info(f"Processed scraped jobs. Added {new_jobs_count} new jobs to DB. Indexed {indexed_jobs_count} new jobs in Qdrant.")

        except Exception as outer_exc:
             logger.error(f"Error during job processing loop: {outer_exc}", exc_info=True)
             db.rollback() # Rollback any potential partial commits from the loop
        finally:
            db.close()
        # --- End Job Processing ---


    except Exception as e:
        logger.error(f"Error during run_all_scrapers_task: {e}", exc_info=True)
        # Depending on retry policy, this might raise the exception to trigger a retry
        raise


@celery_app.task(acks_late=True, name="tasks.process_user_job_matches")
def process_user_job_matches(user_id: int, resume_id: int):
    """ 
    Fetches relevant jobs for a user/resume, checks quotas, 
    creates Application records, and triggers auto-apply tasks.
    """
    logger.info(f"Starting task process_user_job_matches for user_id: {user_id}, resume_id: {resume_id}")
    db = SessionLocal()
    try:
        # --- 1. Get Resume Embedding --- 
        resume = crud.resume.get_resume(db, resume_id=resume_id, owner_id=user_id)
        if not resume:
            logger.error(f"Resume ID {resume_id} not found for user {user_id}. Aborting task.")
            return
        if not resume.embedding:
             logger.error(f"Resume ID {resume_id} has no embedding. Cannot perform matching. Aborting task.")
             return
        resume_embedding = resume.embedding # Assuming embedding is stored correctly

        # --- 2. Find Matched Jobs ---
        logger.info(f"Searching for similar jobs for resume {resume_id} (user {user_id})...")
        # Pass the db session and user_id to the updated search function
        matched_jobs: List[Job] = matching.search_similar_jobs(db=db, resume_embedding=resume_embedding, user_id=user_id)
        if not matched_jobs:
            logger.info(f"No job matches found via Qdrant/DB for user {user_id}, resume {resume_id}.")
            return
        logger.info(f"Found {len(matched_jobs)} potential job matches.")

        # --- 3. Process Matches (Quota Check, Create Application, Trigger Task) ---
        created_count = 0
        quota_exceeded_count = 0
        already_applied_count = 0
        trigger_failed_count = 0

        for job in matched_jobs:
            # --- 3a. Check if application already exists ---
            existing_application = crud.application.get_application_by_details(
                db, user_id=user_id, resume_id=resume_id, job_id=job.id
            )
            if existing_application:
                logger.debug(f"Application already exists for user {user_id}, resume {resume_id}, job {job.id}. Skipping.")
                already_applied_count += 1
                continue

            # --- 3b. Check user quota ---
            has_quota, quota_message = autosubmit.check_user_quota(db, user_id=user_id)
            if not has_quota:
                logger.info(f"Quota exceeded for user {user_id}. Skipping job {job.id}. Reason: {quota_message}")
                quota_exceeded_count += 1
                # Optimization: If quota is exceeded, we can stop processing further matches for this user in this run.
                # However, keep processing all matches for now for simpler logic and logging consistency.
                continue
                # break # Uncomment this line to stop processing if quota is exceeded

            # --- 3c. Create Application Record ---
            logger.info(f"Quota available for user {user_id}. Creating application for job {job.id} ({job.title}).")
            try:
                app_create = schemas.ApplicationCreate(
                    resume_id=resume_id,
                    job_id=job.id,
                    status="PENDING_TRIGGER", # Initial status before task pickup
                    notes="Application created via automated matching task."
                )
                new_application = crud.application.create_application(db=db, application=app_create, user_id=user_id)
                logger.info(f"Created Application record ID: {new_application.id}")

                # --- 3d. Trigger Auto-Apply Task ---
                try:
                    trigger_auto_apply.delay(application_id=new_application.id)
                    logger.info(f"Successfully triggered auto-apply task for application ID: {new_application.id}")
                    created_count += 1
                    # Update status after successful trigger? Optional.
                    # crud.application.update_application_status(db, app_id=new_application.id, status="PENDING_EXECUTION")
                except Exception as trigger_exc:
                    logger.error(f"Failed to trigger auto-apply task for application ID {new_application.id}: {trigger_exc}", exc_info=True)
                    # Optionally update status to reflect trigger failure
                    crud.application.update_application_status(db, app_id=new_application.id, status="TRIGGER_FAILED")
                    trigger_failed_count += 1
                    # Should we rollback the application creation if the trigger fails? Depends on desired behavior.
                    # For now, keep the record with TRIGGER_FAILED status.

            except Exception as app_create_exc:
                logger.error(f"Failed to create Application record for user {user_id}, job {job.id}: {app_create_exc}", exc_info=True)
                db.rollback() # Rollback this specific application creation attempt

        
        logger.info(f"Finished processing matches for user {user_id}, resume {resume_id}. "
                    f"Created/Triggered: {created_count}, Quota Exceeded: {quota_exceeded_count}, Already Existed: {already_applied_count}, Trigger Failed: {trigger_failed_count}")

    except Exception as e:
        logger.error(f"Error during process_user_job_matches for user {user_id}, resume {resume_id}: {e}", exc_info=True)
        db.rollback() # Rollback in case of error during the process
        # Consider raising the exception if retries are desired
        # raise e 
    finally:
        db.close()

