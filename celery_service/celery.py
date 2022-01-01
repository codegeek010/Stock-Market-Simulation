from celery import Celery

from config.config import settings

celery_app = Celery(
    "Stock Market Simulation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "celery_service.tasks.save_transactions",
    ],
)
celery_app.autodiscover_tasks()
