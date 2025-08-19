# bot/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab


# Брокер і бекенд через Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "logisterium",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "bot.services.celery.tasks",  # тут будуть наші таски
    ],
)

# Базові налаштування
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Kyiv",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "sync-client-requests-every-20-seconds": {
        "task": "check_client_sheet_revisions",  # 👈 ім’я як у @celery_app.task
        "schedule": 50.0,  # кожні 20 сек
        "args": (),  # якщо треба — передаєш параметри
    },
}
