import asyncio
from bot.main import main as bot_main
from bot.database.database import engine, Base
import bot.models

import os

if os.getenv("DEBUG") == "1":
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    print("🪲 Debugger attached on port 5678")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def run():
    await init_db()
    await bot_main()


if __name__ == "__main__":
    asyncio.run(run())
