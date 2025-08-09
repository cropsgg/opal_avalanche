from __future__ import annotations

from celery import Celery

from app.core.config import get_settings


_celery_app: Celery | None = None


def get_celery() -> Celery:
    global _celery_app
    if _celery_app is not None:
        return _celery_app
    settings = get_settings()
    app = Celery(
        "opal",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["app.ingestion.pipeline"],
    )
    app.conf.task_routes = {
        "app.ingestion.pipeline.ingest_document": {"queue": "ingest"},
    }
    _celery_app = app
    return app


