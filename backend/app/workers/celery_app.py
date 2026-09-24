from celery import Celery

import app.models  # noqa: F401 — see app/models/__init__.py's docstring
from app.core.config import settings

celery_app = Celery(
    "bidpilot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.ingestion_tasks"],
)
