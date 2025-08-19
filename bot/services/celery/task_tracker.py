# використовуємо той самий Redis, що і Celery
import os
from datetime import timedelta
from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# окремий DB під трекер якщо хочеш: redis://redis:6379/1
# але можна лишити той самий; для простоти лишаю той самий
_redis = Redis.from_url(REDIS_URL, decode_responses=True)

KEY_FMT = "sheet_task:{tg_id}"

def set_sheet_job(tg_id: int, task_id: str, ttl_sec: int = 900) -> None:
    _redis.set(KEY_FMT.format(tg_id=tg_id), task_id, ex=ttl_sec)

def get_sheet_job(tg_id: int) -> str | None:
    return _redis.get(KEY_FMT.format(tg_id=tg_id))

def clear_sheet_job(tg_id: int) -> None:
    _redis.delete(KEY_FMT.format(tg_id=tg_id))

def is_sheet_job_active(tg_id: int) -> bool:
    """
    Перевіряє, чи для цього користувача вже є активна таска формування Google Sheet.
    """
    return get_sheet_job(tg_id) is not None
