from celery import Celery

from ..core.config import settings

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