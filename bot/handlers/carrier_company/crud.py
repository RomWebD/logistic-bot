from sqlalchemy import select
from bot.database.database import async_session
from bot.models import CarrierCompany


async def get_sheet_url_by_telegram_id(telegram_id: int) -> str | None:
    async with async_session() as session:
        result = await session.execute(
            select(CarrierCompany.google_sheet_url).where(
                CarrierCompany.telegram_id == telegram_id
            )
        )
        sheet_url = result.scalar()
        return sheet_url
