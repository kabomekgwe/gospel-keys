"""Celery configuration for background task processing

Handles async audio generation and other long-running tasks.
"""

import logging
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "gospel_keys",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.audio_generation",
        "app.tasks.curriculum_adaptation",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    task_soft_time_limit=540,  # 9 minutes soft limit
    worker_prefetch_multiplier=1,  # Get one task at a time (fair distribution)
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
)

# Periodic tasks (Celery Beat schedule)
celery_app.conf.beat_schedule = {
    # Weekly curriculum adaptation (every Monday at 2:00 AM)
    "weekly-curriculum-adaptation": {
        "task": "app.tasks.curriculum_adaptation.weekly_curriculum_adaptation_task",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),
    },
    # Daily cleanup of failed audio generation tasks (every day at 3:00 AM)
    "daily-audio-cleanup": {
        "task": "app.tasks.audio_generation.cleanup_failed_audio_tasks",
        "schedule": crontab(hour=3, minute=0),
    },
}

logger.info("Celery app configured successfully")
