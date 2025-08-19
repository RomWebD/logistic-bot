# bot/services/redis_consumer.py
import asyncio
import json
import os
import redis.asyncio as aioredis
from bot.services.loader import bot


async def redis_bot_consumer():
    redis_url = os.getenv("REDIS_BOT_URL", "redis://redis_bot:6379/0")
    r = aioredis.from_url(redis_url)

    group = "bot_group"
    stream = "bot:messages"
    consumer = "bot_instance_1"

    # створюємо consumer group (ігноруємо помилку якщо вже є)
    try:
        await r.xgroup_create(stream, group, id="0", mkstream=True)
    except Exception:
        pass

    while True:
        # читаємо події (блокуємось до 5 сек)
        resp = await r.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={stream: ">"},
            count=10,
            block=5000,
        )
        if not resp:
            continue

        for _stream, msgs in resp:
            for msg_id, fields in msgs:
                tg_id = int(fields[b"tg_id"].decode())
                text = fields[b"text"].decode()
                kb = None
                if b"kb" in fields:
                    kb = json.loads(fields[b"kb"].decode())
                try:
                    await bot.send_message(tg_id, text, reply_markup=kb)
                    # підтверджуємо обробку
                    await r.xack(stream, group, msg_id)
                except Exception as e:
                    print(f"❌ Failed to send: {e}")
