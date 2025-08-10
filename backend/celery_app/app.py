from celery import Celery

from backend.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "tg_webapp",
    broker=settings.CELERY_BROKER_URL_PROPERTY,
    backend=settings.CELERY_RESULT_BACKEND_PROPERTY,
    include=["backend.celery_app.tasks"],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks()
