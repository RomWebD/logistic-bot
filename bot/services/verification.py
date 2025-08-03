from sqlalchemy import select
from bot.models.carrier_company import CarrierCompany
from bot.database.database import async_session

async def is_verified_carrier(chat_id: int) -> bool:
    async with async_session() as session:
        result = await session.scalar(
            select(CarrierCompany).where(
                CarrierCompany.telegram_id == chat_id,
                CarrierCompany.is_verify.is_(True),
            )
        )
        return result is not None
