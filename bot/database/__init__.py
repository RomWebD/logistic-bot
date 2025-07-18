import asyncio
from bot.database.database import engine, Base


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ DB initialized!")


if __name__ == "__main__":
    asyncio.run(init_db())
