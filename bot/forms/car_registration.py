# bot/forms/vehicle_registration.py
from __future__ import annotations
from typing import Any, List
from aiogram.types import Message

from bot.forms.base import BaseForm, FormField
from bot.database.database import get_session
from bot.models.transport_vehicle import TransportVehicle
# from bot.repositories.carrier_company_repository import CarrierCompanyRepository
from bot.repositories.google_sheet_repository import GoogleSheetRepository
from bot.models.google_sheets_binding import OwnerType, SheetType

# Celery таска (нижче додам реалізацію)
from bot.services.celery.tasks import append_vehicle_to_sheet


# --- валідації/нормалізації ---
def _not_empty(v: Any) -> str | None:
    if v is None or (isinstance(v, str) and not v.strip()):
        return "Поле не може бути порожнім"
    return None


def _normalize_float(v: str) -> float | str:
    s = (v or "").lower().replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except Exception:
        return v


def _validate_float(v: Any) -> str | None:
    if isinstance(v, float) and v >= 0:
        return None
    return "Вкажіть число (0 або більше)."


def _validate_phone(v: str) -> str | None:
    s = (v or "").replace(" ", "")
    return None if (len(s) >= 9 and s[0].isdigit()) else "Невірний номер телефону"


# значення з твого старого флоу
LOADING_OPTIONS: List[tuple[str, str]] = [
    ("side", "Бік"),
    ("top", "Верх"),
    ("back", "Зад"),
]

VEHICLE_TYPES: List[tuple[str, str]] = [
    ("Тент", "Тент"),
    ("Рефрижератор", "Рефрижератор"),
    ("Цистерна", "Цистерна"),
    ("Контейнеровоз", "Контейнеровоз"),
    ("Інше", "Інше (ввести вручну)"),
]


class VehicleRegistrationForm(BaseForm):
    summary_header = "🚚 <b>Додавання транспортного засобу:</b>"
    include_progress = True

    fields = [
        # 1) тип ТЗ (select)
        FormField(
            name="vehicle_type",
            title="Тип транспорту",
            kind="select",
            prompt="Оберіть тип транспорту:",
            options=VEHICLE_TYPES,
            allow_skip=False,
        ),
        # 1.1) якщо обрав "Інше" — просимо ввести вручну
        FormField(
            name="vehicle_type_other",
            title="Свій тип транспорту",
            kind="text",
            prompt="Введіть тип транспорту:",
            allow_skip=True,
        ),
        # 2) номер(и) авто: підтримуємо перелік через / або пробіли,
        #    ми створимо запис(и) по кожному номеру
        FormField(
            name="registration_numbers",
            title="Номер(и) авто",
            kind="text",
            prompt="Введіть номер(и) авто (напр.: <code>АС2369СА / АС5729ХР</code>)",
            validator=_not_empty,
        ),
        # 3) вантажопідйомність (т)
        FormField(
            name="load_capacity_tons",
            title="Вантажопідйомність, т",
            kind="text",
            prompt="Введіть вантажопідйомність у тоннах (напр.: <code>23</code>):",
            normalizer=_normalize_float,
            validator=_validate_float,
        ),
        # 4) об’єм (м³) — опційно
        FormField(
            name="body_volume_m3",
            title="Обʼєм, м³",
            kind="text",
            prompt="Введіть обʼєм у м³ (напр.: <code>86</code>) або пропустіть:",
            normalizer=_normalize_float,
            allow_skip=True,
            # якщо юзер введе сміття — хай падає валідація лише коли не пусто
            validator=lambda v: None
            if (v == "" or isinstance(v, float))
            else "Вкажіть число або пропустіть",
        ),
        # 5) спосіб завантаження (multiselect)
        FormField(
            name="loading_type",
            title="Спосіб завантаження",
            kind="multiselect",
            prompt="Оберіть спосіб завантаження:",
            options=LOADING_OPTIONS,
            allow_skip=True,
        ),
        # 6) ПІБ водія
        FormField(
            name="driver_fullname",
            title="ПІБ водія",
            kind="text",
            prompt="Введіть ПІБ водія:",
            allow_skip=True,
        ),
        # 7) Телефон водія
        FormField(
            name="driver_phone",
            title="Телефон водія",
            kind="text",
            prompt="Введіть номер телефону водія:",
            validator=lambda v: None if v in ("", None) else _validate_phone(v),
            allow_skip=True,
        ),
    ]

    icons = {
        "vehicle_type": "🚛",
        "vehicle_type_other": "✍️",
        "registration_numbers": "🔢",
        "load_capacity_tons": "⚖️",
        "body_volume_m3": "📦",
        "loading_type": "📥",
        "driver_fullname": "👤",
        "driver_phone": "📞",
    }

    async def on_submit(self, data: dict, message: Message):
        """
        1) нормалізуємо вхідні поля (тип, номери, multiselect)
        2) створюємо 1..N записів TransportVehicle (якщо вказано кілька номерів)
        3) гарантуємо Google Sheet (Автопарк) для перевізника і додаємо рядки
        """
        tg_id: int | None = data.get("tg_id")
        if tg_id is None:
            raise RuntimeError("tg_id is required in state for VehicleRegistrationForm")

        # vehicle_type: якщо обрано "Інше", підміняємо на manual
        vehicle_type = data.get("vehicle_type") or ""
        if vehicle_type == "Інше":
            vt_other = (data.get("vehicle_type_other") or "").strip()
            vehicle_type = vt_other or "Інше"

        # розпарсити номери авто: підтримуємо "/", ",", пробіли
        raw = (
            (data.get("registration_numbers") or "").replace(",", " ").replace("/", " ")
        )
        numbers = [p.strip().upper() for p in raw.split() if p.strip()]
        if not numbers:
            await message.answer("❌ Не знайдено жодного номера авто.")
            return

        # multiselect loading_type -> рядок
        loading_list = data.get("loading_type") or []
        # в твоєму старому флоу відображались "Бік/Верх/Зад" — збережемо так само
        loading_str = (
            ", ".join(
                label for val, label in LOADING_OPTIONS if val in set(loading_list)
            )
            or None
        )

        load_capacity = data.get("load_capacity_tons")
        volume = data.get("body_volume_m3")
        driver_fullname = (data.get("driver_fullname") or "").strip() or None
        driver_phone = (data.get("driver_phone") or "").strip() or None

        created = []

        async with get_session() as session:
            # знайти перевізника за tg_id
            carrier_repo = CarrierCompanyRepository(session)
            carrier = await carrier_repo.get_by_telegram_id(tg_id)
            if not carrier:
                await message.answer("❌ Перевізника не знайдено. Почніть з /start.")
                return

            # створюємо записи (уникатимемо дубля за номером)
            for reg_num in numbers:
                # якщо є унікальний індекс — просто пробуємо створити/пропустити
                # можна перевірити вручну, щоб не ловити IntegrityError
                exists = (
                    await session.scalar(
                        TransportVehicle.select().where(
                            TransportVehicle.registration_number == reg_num
                        )
                    )
                    if hasattr(TransportVehicle, "select")
                    else None
                )  # на випадок різних базових моделей
                if exists:
                    continue

                tv = TransportVehicle(
                    carrier_company_id=carrier.id,
                    vehicle_type=vehicle_type,
                    registration_number=reg_num,
                    load_capacity_tons=float(load_capacity),
                    body_volume_m3=(
                        float(volume) if isinstance(volume, float) else None
                    ),
                    loading_equipment=loading_str,  # можна JSON, але текст достатньо
                    driver_fullname=driver_fullname,
                    driver_phone=driver_phone,
                    is_active=True,
                )
                session.add(tv)
                created.append(tv)

            if not created:
                await message.answer(
                    "ℹ️ Усі вказані номери вже існують у вашому автопарку."
                )
                return

            await session.commit()
            for tv in created:
                await session.refresh(tv)

            # гарантуємо binding для "Автопарк" і пускаємо Celery писати рядок(и)
            sheet_repo = GoogleSheetRepository(session)
            binding = await sheet_repo.get_by_owner_and_type(
                telegram_id=tg_id,
                owner_type=OwnerType.CARRIER,
                sheet_type=SheetType.VEHICLES,
            )
            if not binding:
                await sheet_repo.create_or_update(
                    telegram_id=tg_id,
                    owner_type=OwnerType.CARRIER,
                    sheet_type=SheetType.VEHICLES,
                    sheet_id=None,
                    sheet_url=None,
                )
                await session.commit()

            # шлемо таску для кожного авто
            # for tv in created:
            #     append_vehicle_to_sheet.delay(tg_id=tg_id, vehicle_id=tv.id)

        await message.answer(
            f"✅ Додано {len(created)} транспортн[ий/і] засіб(и) у ваш автопарк."
        )
