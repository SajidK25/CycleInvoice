"""Celery settings for the Cycle Invoice project."""
import os

from celery.schedules import crontab

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://:foobared@192.168.0.37:6379/0")

CELERY_TIMEZONE = "Europe/Zurich"

CELERY_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = 300  # 5 minutes

CELERY_BEAT_SCHEDULE = {
    "process-subscriptions-daily": {
        "task": "sale.tasks.subscription_processing_to_document_items",
        "schedule": crontab(hour=0, minute=0),
    },
}
