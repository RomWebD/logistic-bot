import os
import json
import redis

r_bot = redis.Redis.from_url(os.getenv("REDIS_BOT_URL", "redis://redis_bot:6379/0"))


def queue_bot_message(tg_id: int, text: str, kb: dict | None = None):
    data = {"tg_id": tg_id, "text": text}
    if kb:
        data["kb"] = json.dumps(kb)
    r_bot.xadd("bot:messages", data, maxlen=1000, approximate=True)
