from sqlalchemy import select, func, update
from bot.database.database import get_session
from bot.handlers.client.utils import _now_utc, _parse_google_time
from bot.models import Client
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from typing import List, Optional, Tuple

from bot.models.client import SheetStatus
from bot.models.sheet_binding import SheetBinding, SheetKind
from bot.models.shipment_request import Shipment_request

from typing import Literal
from bot.services.google_services.sheets_client import RequestSheetManager
from sqlalchemy.ext.asyncio import AsyncSession


async def sync_requests_from_sheets(client: Client):
    """Синхронізує заявки з Google Sheets у БД, якщо в БД пусто."""
    manager = RequestSheetManager()

    # переконуємось, що таблиця існує (або створюємо)
    sheet_id, sheet_url = manager.ensure_request_sheet_for_client(
        tg_id=client.telegram_id,
        client_full_name=client.full_name,
        client_email=client.email,
        google_sheet_id=client.google_sheet_id,
        google_sheet_url=client.google_sheet_url,
    )

    # витягуємо всі рядки з аркуша "Заявки"
    rows = (
        manager.svc_sheets.sheets.spreadsheets()
        .values()
        .get(
            spreadsheetId=sheet_id,
            range="Заявки!A2:Z",  # A1 — це хедери
        )
        .execute()
        .get("values", [])
    )

    if not rows:
        return 0  # нічого немає

    async with get_session() as session:
        for row in rows:
            # перетворюємо рядок у модель
            req = Shipment_request(
                client_telegram_id=client.telegram_id,
                from_city=row[0],
                to_city=row[1],
                date_text=row[3],  # або row[2]/row[3] залежно від мапи
                cargo_type=row[4],
                volume=row[5],
                weight=row[6],
                loading=row[7],
                unloading=row[8],
                price=int(row[9]) if row[9].isdigit() else 0,
                description=row[10] if len(row) > 10 else None,
            )
            session.add(req)
        await session.commit()

    return len(rows)


# ✅ Універсальна функція для отримання клієнта
async def get_client_by_telegram_id(
    telegram_id: int, session: AsyncSession | None = None
) -> Optional[Client]:
    if session is not None:
        res = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        return res.scalar_one_or_none()

    async with get_session() as session:
        res = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        return res.scalar_one_or_none()


async def get_all_clients_with_sheets() -> List[Client]:
    """Повертає всіх клієнтів, у кого є Google Sheet (id не NULL)."""
    async with get_session() as session:
        res = await session.execute(
            select(Client).where(Client.google_sheet_id.isnot(None))
        )
        return res.scalars().all()


async def update_client_sheet_by_telegram(
    telegram_id: int, sheet_id: str, sheet_url: str
) -> None:
    async with get_session() as session:
        await session.execute(
            update(Client)
            .where(Client.telegram_id == telegram_id)
            .values(google_sheet_id=sheet_id, google_sheet_url=sheet_url)
        )
        await session.commit()


async def count_requests_by_telegram(telegram_id: int) -> int:
    async with get_session() as session:
        res = await session.execute(
            select(func.count(Shipment_request.id)).where(
                Shipment_request.client_telegram_id == telegram_id
            )
        )
        return int(res.scalar() or 0)


async def get_request_by_id(
    request_id: int, session: AsyncSession | None = None
) -> Optional[Shipment_request]:
    """
    Повертає Shipment_request за ID.
    Якщо сесія передана ззовні — використовує її, інакше створює власну.
    """
    if session is not None:
        res = await session.execute(
            select(Shipment_request).where(Shipment_request.id == request_id)
        )
        return res.scalar_one_or_none()

    # якщо сесію не передали — створюємо власну
    async with get_session() as session:
        res = await session.execute(
            select(Shipment_request).where(Shipment_request.id == request_id)
        )
        return res.scalar_one_or_none()


async def get_client_and_request(
    telegram_id: int,
    request_id: int,
    session: AsyncSession | None = None,
) -> Tuple[Optional[Client], Optional[Shipment_request]]:
    if session is None:
        async with get_session() as session:
            return await get_client_and_request(telegram_id, request_id, session)

    client = await get_client_by_telegram_id(telegram_id, session=session)

    res_r = await session.execute(
        select(Shipment_request).where(Shipment_request.id == request_id)
    )
    req = res_r.scalar_one_or_none()

    return client, req


async def mark_sheet_opened(
    tg_id: int,
    sheet_kind: Literal["requests", "vehicles"],
    revision_id: Optional[str],
    modified_time: Optional[str],
    user_email: Optional[str],
    user_name: Optional[str],
) -> SheetBinding:
    """
    Фіксує факт входу користувача у розділ з Google Sheets:
    - оновлює last_opened_at (зараз),
    - записує останню відому ревізію (revision_id) та хто її зробив,
    - НЕ робить синк і НЕ змінює last_synced_*.

    Якщо биндингу ще не існує — створює його (sheet_id/url підтягне з Client).
    """
    async with get_session() as session:
        # 1) знайдемо/створимо binding
        binding: Optional[SheetBinding] = await session.scalar(
            select(SheetBinding).where(
                SheetBinding.owner_telegram_id == tg_id,
                SheetBinding.kind == SheetKind(sheet_kind),
            )
        )
        if not binding:
            # спробуємо підтягнути sheet_id/url з клієнта (на випадок коли не створили раніше)
            client: Optional[Client] = await session.scalar(
                select(Client).where(Client.telegram_id == tg_id)
            )
            if not client:
                raise ValueError(f"Client with telegram_id={tg_id} not found")

            binding = SheetBinding(
                owner_telegram_id=tg_id,
                kind=SheetKind(sheet_kind),
                sheet_id=client.google_sheet_id,
                sheet_url=client.google_sheet_url,
                created_at=_now_utc(),
                updated_at=_now_utc(),
            )
            session.add(binding)

        # 2) оновимо поля "відкриття"
        binding.last_opened_at = _now_utc()
        binding.last_opened_revision = revision_id
        binding.last_opened_modified_time = _parse_google_time(modified_time)
        binding.last_opened_by_email = user_email
        binding.last_opened_by_name = user_name
        binding.updated_at = _now_utc()

        await session.commit()
        await session.refresh(binding)
        return binding


async def update_binding_after_sync(
    binding_id: int,
    *,
    last_synced_revision: Optional[str],
    clear_cooldown: bool = True,
    mark_not_in_progress: bool = True,
) -> SheetBinding:
    """
    Позначає у прив’язці, що синк завершено:
    - last_synced_at = now,
    - last_synced_revision = переданий,
    - (опц.) sync_in_progress = False,
    - (опц.) cooldown_until = NULL.

    :param binding_id: ID запису у sheet_bindings
    :param last_synced_revision: ревізія, на якій завершили синк (може бути None, якщо skipped)
    :param clear_cooldown: очистити cooldown_until (дефолт: так)
    :param mark_not_in_progress: зняти прапор sync_in_progress (дефолт: так)
    """

    async with get_session() as session:
        binding = await session.get(SheetBinding, binding_id)
        if not binding:
            raise ValueError(f"SheetBinding id={binding_id} not found")

        binding.last_synced_at = _now_utc()
        binding.last_synced_revision = last_synced_revision
        if mark_not_in_progress:
            binding.sync_in_progress = False
        if clear_cooldown:
            binding.cooldown_until = None
        binding.updated_at = _now_utc()

        await session.commit()
        await session.refresh(binding)
        return binding


async def ensure_client_sheet_binding(
    telegram_id: int,
    new_sheet_id: str,
    new_sheet_url: str,
    session: AsyncSession | None = None,
) -> bool:
    """
    Повертає True, якщо значення змінились і ми оновили БД.
    """
    if session is None:
        async with get_session() as session:
            return await ensure_client_sheet_binding(
                telegram_id, new_sheet_id, new_sheet_url, session
            )

    client = await get_client_by_telegram_id(telegram_id, session=session)
    if not client:
        return False

    if (
        client.google_sheet_id != new_sheet_id
        or client.google_sheet_url != new_sheet_url
    ):
        await session.execute(
            update(Client)
            .where(Client.id == client.id)
            .values(google_sheet_id=new_sheet_id, google_sheet_url=new_sheet_url)
        )
        await session.commit()
        return True

    return False


async def update_sheet_status(
    telegram_id: int,
    status: SheetStatus,
    url: str | None = None,
    sheet_id: str | None = None,
    session: AsyncSession = None,
):
    stmt = (
        update(Client)
        .where(Client.telegram_id == telegram_id)
        .values(
            sheet_status=status,
            google_sheet_url=url,
            google_sheet_id=sheet_id,
        )
    )
    await session.execute(stmt)
    await session.commit()


# utils.py або crud.py
def build_vehicle_sheet_markup(sheet_url: str) -> InlineKeyboardMarkup:
    if sheet_url:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Мої заявки", url=sheet_url)],
                [
                    InlineKeyboardButton(
                        text="➕ Створити нову заявку",
                        callback_data="carrier_add_new_car",
                    )
                ],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(
                text="➕ Створити нову заявку",
                callback_data="client_create_new_request",
            )
        ],
    )
