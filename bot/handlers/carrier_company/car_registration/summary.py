from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram.fsm.context import FSMContext

from bot.models.TransportVehicle import TransportVehicle
from bot.services.verification import get_carrier_by_telegram_id

from .fsm import get_progress_bar
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from bot.database.database import async_session

router = Router()


async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    summary = (
        # f"🚚 **Перевірте введені дані:**\n"
        f"Тип: {data.get('car_type') or '-'}\n"
        f"Номер(и): {data.get('plate_number') or '-'}\n"
        f"Вантажопідйомність: {data.get('weight_capacity') or '-'}\n"
        f"Обʼєм: {data.get('volume') or '-'}\n"
        f"Завантаження: {', '.join(data.get('loading_type') or [])}\n"
        f"Водій: {data.get('driver_fullname') or '-'}\n"
        f"Телефон: {data.get('driver_phone') or '-'}\n" + get_progress_bar(data)
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Зберегти", callback_data="car_save"),
                InlineKeyboardButton(text="✏️ Редагувати", callback_data="car_edit"),
            ],
            [InlineKeyboardButton(text="🚫 Скасувати додавання", callback_data="menu")],
        ]
    )
    # 1. Спочатку — самі дані (без кнопок)
    await message.answer(
        f"<b>🚚 Перевірте введені дані:</b>\n\n<pre>{summary}</pre>", parse_mode="HTML"
    )

    # 2. Потім — кнопки
    await message.answer("⬇️ Оберіть дію нижче:", reply_markup=keyboard)
    # Для того, щоб зберегти в чаті поточні заповнені дані


@router.callback_query(F.data == "car_save")
async def save_car(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    telegram_id = callback.from_user.id

    # Витягуємо перевізника з telegram_id
    carrier = await get_carrier_by_telegram_id(telegram_id)
    if not carrier:
        await callback.message.edit_text("❌ Помилка: не знайдено профіль перевізника.")
        return

    try:
        # Перевіряємо обов’язкові поля
        required_fields = ["car_type", "plate_number", "weight_capacity"]
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Обов’язкове поле '{field}' не заповнене")

        # Створення об’єкта моделі
        vehicle = TransportVehicle(
            vehicle_type=data.get("car_type"),
            registration_number=data.get("plate_number"),
            load_capacity_tons=(data.get("weight_capacity")),
            body_volume_m3=(data.get("volume")) if data.get("volume") else None,
            special_equipment=", ".join(data.get("loading_type") or []),
            driver_fullname=data.get("driver_fullname") or None,
            driver_phone=data.get("driver_phone") or None,
            carrier_company_id=carrier.id,
        )

        # Запис у БД
        async with async_session() as session:
            session.add(vehicle)
            await session.commit()

        await callback.message.edit_text(
            "✅ Транспорт успішно додано!", reply_markup=None
        )
        await state.clear()

    except ValueError as ve:
        await callback.message.edit_text(f"❌ Помилка: {ve}")
    except IntegrityError:
        await callback.message.edit_text(
            "❌ Помилка: Транспорт з таким номером уже існує."
        )
    except SQLAlchemyError as e:
        await callback.message.edit_text(
            "❌ Сталася помилка збереження. Спробуйте пізніше."
        )
        # Тут можна додатково залогувати e
    except Exception as e:
        await callback.message.edit_text(
            "❌ Невідома помилка. Зверніться до підтримки."
        )
        # Тут також можеш логувати
