"""
Celery application configuration for Anki Compendium.

Handles distributed task processing for PDF-to-Anki deck generation.
"""

import logging

from celery import Celery
from celery.signals import after_setup_logger, setup_logging

from app.config import settings

# Configure root logger for Celery
logger = logging.getLogger(__name__)


@setup_logging.connect
def setup_celery_logging(**kwargs):
    """Configure logging for Celery."""
    pass  # Use the app's logging configuration


@after_setup_logger.connect
def after_celery_logger_setup(logger, *args, **kwargs):
    """Configure logger after Celery setup."""
    # Add custom handlers if needed
    pass


# Create Celery application
celery_app = Celery(
    "anki_compendium",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery Configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task Tracking
    task_track_started=True,
    task_send_sent_event=True,
    
    # Task Timeouts
    task_time_limit=7200,  # 2 hours hard limit
    task_soft_time_limit=6900,  # 1h 55m soft limit (sends signal)
    
    # Task Execution
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,  # Reject if worker crashes
    worker_prefetch_multiplier=1,  # Fetch one task at a time (for long tasks)
    
    # Task Results
    result_expires=86400,  # Results expire after 24 hours
    result_extended=True,  # Store additional task metadata
    
    # Worker Configuration
    worker_max_tasks_per_child=50,  # Restart worker after N tasks (memory management)
    worker_disable_rate_limits=False,
    
    # Task Routing
    task_routes={
        "app.workers.tasks.process_pdf_task": {
            "queue": "pdf_processing",
            "routing_key": "pdf.process",
        },
    },
    
    # Retry Policy
    task_autoretry_for=(Exception,),
    task_retry_kwargs={"max_retries": 3, "countdown": 300},  # 5 minutes between retries
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)

# Auto-discover tasks from workers module
celery_app.autodiscover_tasks(["app.workers"])

logger.info("Celery application initialized")
