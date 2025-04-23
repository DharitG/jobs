import logging # Add logging import
from celery import Celery

from ..core.config import settings

# --- Sentry Integration ---
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

logger = logging.getLogger(__name__) # Add logger

if settings.SENTRY_DSN:
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                CeleryIntegration(monitor_beat_tasks=True), # Monitor beat tasks as well
            ],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0, # Adjust as needed
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0, # Adjust as needed
            # Consider adding environment, release from settings if available
            # environment=settings.ENVIRONMENT,
            # release=settings.APP_VERSION,
        )
        logger.info("Sentry SDK initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry SDK: {e}", exc_info=True)
else:
    logger.info("SENTRY_DSN not found in settings. Skipping Sentry initialization.")
# --- End Sentry Integration ---


# Initialize Celery
# The first argument is the name of the current module, useful for auto-generating task names.
# The broker and backend URLs are taken from the settings.
# The include argument tells Celery where to look for task modules.
celery_app = Celery(
    "jobbright_worker", 
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"] # Point to the tasks module
)

# Optional Celery configuration (can be loaded from settings too)
from celery.schedules import crontab # Import crontab

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Add other configurations like rate limits later if needed
    task_acks_late = True, # Example: Ensure tasks only ack after completion/failure
    worker_prefetch_multiplier = 1, # Example: Ensure worker only takes 1 task at a time if tasks are long-running
    # task_routes = {
    #     'app.workers.tasks.process_payment': {'queue': 'payments'},
    # }
    beat_schedule = {
        'run-scrapers-every-6-hours': {
            'task': 'tasks.run_all_scrapers', # The name of the task defined in tasks.py
            'schedule': crontab(minute=0, hour='*/6'), # Run every 6 hours (at 00:00, 06:00, 12:00, 18:00 UTC)
            # Alternatively, use seconds: 'schedule': 6 * 60 * 60.0, # Run every 6 hours (in seconds)
            # 'args': (), # Add arguments if the task requires any
        },
    }
)

if __name__ == "__main__":
    # This allows running the worker directly for testing
    # Command: celery -A app.workers.celery_app worker --loglevel=info
    celery_app.start() # Note: Usually run via CLI command, not directly started like this