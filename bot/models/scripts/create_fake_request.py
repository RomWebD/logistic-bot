# scripts/create_fake_request.py

import asyncio
import datetime
from bot.models.shipment_request import Shipment_request
from bot.database.database import get_session
from bot.services.notifier import notify_carriers
from bot.main import bot  # якщо бот вже створений


async def main():
    fake = Shipment_request(
        route="Київ → Львів",
        date=datetime(2025, 7, 20, 10, 0),
        cargo_type="Побутова техніка, упакована на палетах",
        volume="6 палет",
        weight="2.2 т",
        loading="Рокла, рампа",
        unloading="Ручне",
        price=8000,
    )

    async for session in get_session():
        session.add(fake)
        await session.commit()

    await notify_carriers(bot, fake)


if __name__ == "__main__":
    asyncio.run(main())
