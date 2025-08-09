from __future__ import annotations

from app.core.tasks import celery_app


if __name__ == "__main__":
    celery_app.start()


