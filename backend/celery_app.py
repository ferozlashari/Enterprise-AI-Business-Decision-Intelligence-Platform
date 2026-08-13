from celery import Celery

from config.settings import settings

celery = Celery(
    "enterprise_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Karachi",
    enable_utc=False,
)

# Auto-discover tasks registered under backend.tasks so the
# worker picks them up whether it's started with -A backend.celery_app
# from the repo root (as in docker-compose) or another entrypoint.
celery.autodiscover_tasks(["backend.tasks"])
