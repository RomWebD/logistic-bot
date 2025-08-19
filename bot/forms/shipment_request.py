from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass

from bot.forms.base import BaseForm, FormField
from bot.database.database import get_session
from bot.models.shipment_request import Shipment_request

# Celery таска: забезпечити файл і дописати рядок
from bot.services.celery.tasks import append_request_to_sheet
from aiogram.types import Message


def _not_empty(v: Any) -> str | None:
    if v is None or (isinstance(v, str) and not v.strip()):
        return "Поле не може бути порожнім"
    return None


def _normalize_price(v: str) -> int | str:
    # допускаємо "8 000", "8000 грн", "8k"
    s = (v or "").lower().replace("грн", "").replace(" ", "")
    if s.endswith("k"):
        s = s[:-1] + "000"
    try:
        return int(s)
    except Exception:
        return v  # нехай впаде на валідації


def _validate_price(v: Any) -> str | None:
    if isinstance(v, int):
        return None
    return "Вкажіть ціну числом (наприклад: 8000)."


class ShipmentRequestForm(BaseForm):
    summary_header = "📦 <b>Нова заявка на перевезення:</b>"
    include_progress = True

    fields = [
        FormField(
            name="from_city",
            title="Маршрут (звідки)",
            kind="text",
            prompt="🚚 Звідки потрібно забрати вантаж? (напр.: <code>Київ</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="to_city",
            title="Маршрут (куди)",
            kind="text",
            prompt="🏁 Куди потрібно доставити вантаж? (напр.: <code>Львів</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="date",
            title="Дата подачі",
            kind="text",
            prompt="📅 Введіть дату подачі (напр.: <code>20 липня до 10:00</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="cargo_type",
            title="Тип вантажу",
            kind="text",
            prompt="📦 Введіть тип вантажу (напр.: <code>Побутова техніка, палети</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="volume",
            title="Обʼєм",
            kind="text",
            prompt="📦 Введіть обʼєм (напр.: <code>6 палет</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="weight",
            title="Вага",
            kind="text",
            prompt="⚖️ Введіть вагу (напр.: <code>2.2 т</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="loading",
            title="Завантаження",
            kind="text",
            prompt="📥 Як буде завантаження? (напр.: <code>рокла, рампа</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="unloading",
            title="Вивантаження",
            kind="text",
            prompt="📤 Як буде вивантаження? (напр.: <code>ручне</code>)",
            validator=_not_empty,
        ),
        FormField(
            name="price",
            title="Ціна",
            kind="text",
            prompt="💰 Введіть бажану ціну (напр.: <code>8000 грн</code>)",
            normalizer=_normalize_price,
            validator=_validate_price,
        ),
    ]

    icons = {
        "from_city": "🧭",
        "to_city": "📍",
        "date": "📅",
        "cargo_type": "📦",
        "volume": "🧱",
        "weight": "⚖️",
        "loading": "📥",
        "unloading": "📤",
        "price": "💰",
    }

    async def on_submit(self, data: dict, message: Message):
        """
        1) зберігаємо в БД Shipment_request
        2) фоном: ensure Google Sheet (+оновити БД, якщо файл створився новий) і додати рядок
        """
        tg_id: int | None = data.get("tg_id")
        if tg_id is None:
            # захисний варіант: якщо забудемо покласти tg_id в state перед стартом форми
            raise RuntimeError(
                "tg_id is required in state data for ShipmentRequestForm"
            )

        async with get_session() as session:
            req = Shipment_request(
                client_telegram_id=tg_id,
                from_city=data.get("from_city"),
                to_city=data.get("to_city"),
                date=data.get("date"),
                date_text=data.get("date"),
                cargo_type=data.get("cargo_type"),
                volume=data.get("volume"),
                weight=data.get("weight"),
                loading=data.get("loading"),
                unloading=data.get("unloading"),
                price=data.get("price"),
            )
            session.add(req)
            await session.commit()
            await session.refresh(req)

            # фонова Celery-таска: забезпечити файл і додати рядок
            append_request_to_sheet.delay(tg_id=tg_id, request_id=req.id)
