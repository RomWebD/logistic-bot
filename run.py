import asyncio
from bot.main import main as bot_main
from bot.database.database import engine, Base
import bot.models


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def run():
    await init_db()
    await bot_main()


if __name__ == "__main__":
    asyncio.run(run())
