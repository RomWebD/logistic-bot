# bot/celery_app.py
import os
from celery import Celery

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
