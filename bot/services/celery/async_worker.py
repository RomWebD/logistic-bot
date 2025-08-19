# bot/async_worker.py
import asyncio
import json
import os
import redis.asyncio as aioredis
from bot.services.loader import bot


async def bot_consumer():
    redis_url = os.getenv("REDIS_BOT_URL", "redis://redis_bot:6379/0")
    r = aioredis.from_url(redis_url)
    last_id = "0"

    while True:
        # Читаємо нові повідомлення (блокуємось поки нема)
        msgs = await r.xread({"bot:messages": last_id}, block=0, count=1)
        for stream, entries in msgs:
            for msg_id, fields in entries:
                tg_id = int(fields[b"tg_id"].decode())
                text = fields[b"text"].decode()
                kb = None
                if b"kb" in fields:
                    kb = json.loads(fields[b"kb"].decode())
                await bot.send_message(tg_id, text, reply_markup=kb)
                last_id = msg_id


async def main():
    await asyncio.gather(
        bot_consumer(),
        # тут же можна запустити твій aiogram Dispatcher якщо треба
    )


if __name__ == "__main__":
    asyncio.run(main())
