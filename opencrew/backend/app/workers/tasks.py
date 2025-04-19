import logging

from .celery_app import celery_app # Import the configured Celery app
from ..services import autosubmit, scraping, matching # Import scraping and matching services
from ..db.session import SessionLocal # Needed for DB operations within tasks
from .. import crud, schemas # Needed for DB operations

logger = logging.getLogger(__name__)

@celery_app.task(acks_late=True, name="tasks.trigger_auto_apply") # Use explicit name
def trigger_auto_apply(application_id: int):
    """Celery task to trigger the auto-application process for a given application ID."""
    logger.info(f"Received task trigger_auto_apply for application_id: {application_id}")
    try:
        # Call the actual auto-submit function from the service
        autosubmit.apply_to_job(application_id=application_id)
        logger.info(f"Successfully processed task trigger_auto_apply for application_id: {application_id}")
        # The result/status update should happen within apply_to_job or via another mechanism
    except Exception as e:
        # Log the error; Celery can handle retries based on configuration if needed
        logger.error(f"Error processing task trigger_auto_apply for application_id: {application_id}. Error: {e}", exc_info=True)
        # Depending on retry policy, this might raise the exception to trigger a retry
        raise

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
