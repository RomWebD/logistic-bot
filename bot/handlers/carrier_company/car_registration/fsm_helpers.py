from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from .fsm import RegisterCar, ALL_FIELDS

# Підказки до кожного поля
FIELD_PROMPTS = {
    "car_type": "Оберіть тип транспорту:",
    "plate_number": "Введіть номер(и) авто (наприклад: АС2369СА / АС5729ХР):",
    "weight_capacity": "Введіть вантажопідйомність (наприклад: 23 тони):",
    "volume": "Введіть обʼєм (наприклад: 86 м3):",
    "driver_fullname": "Введіть ПІБ водія:",
    "driver_phone": "Введіть номер телефону водія:",
}
FIELD_LABELS = {
    "car_type": "Тип транспорту",
    "plate_number": "Номер(и) авто",
    "weight_capacity": "Вантажопідйомність",
    "volume": "Обʼєм",
    "loading_type": "Спосіб завантаження",
    "driver_fullname": "ПІБ водія",
    "driver_phone": "Телефон водія",
}


def get_car_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Тент", callback_data="type_Тент"),
                InlineKeyboardButton(
                    text="Рефрижератор", callback_data="type_Рефрижератор"
                ),
                InlineKeyboardButton(text="Цистерна", callback_data="type_Цистерна"),
            ],
            [
                InlineKeyboardButton(
                    text="Контейнеровоз", callback_data="type_Контейнеровоз"
                ),
                InlineKeyboardButton(
                    text="Інше (ввести вручну)", callback_data="type_other"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏭️ Пропустити поточний пункт", callback_data="skip_car_type"
                ),
            ],
        ]
    )


def get_progress_bar(data: dict) -> str:
    filled = sum(1 for field in ALL_FIELDS if data.get(field))
    percent = int((filled / len(ALL_FIELDS)) * 100)
    blocks = int(percent / 10)
    return f"\n\n📊 Прогрес: [{'■' * blocks}{'□' * (10 - blocks)}] {percent}%"


async def ask_for_step(state: FSMContext, field: str, message: Message):
    await state.set_state(getattr(RegisterCar, field))
    if field == "car_type":
        await message.answer(
            "🚛 Оберіть тип транспорту:", reply_markup=get_car_type_keyboard()
        )
        return
    # Спеціальна логіка для способу завантаження
    if field == "loading_type":
        await state.update_data(loading_type=set())
        await message.answer(
            "Оберіть спосіб завантаження:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Бік", callback_data="load_side")],
                    [InlineKeyboardButton(text="Верх", callback_data="load_top")],
                    [InlineKeyboardButton(text="Зад", callback_data="load_back")],
                    [
                        InlineKeyboardButton(
                            text="✅ Завершити вибір", callback_data="load_done"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⏭️ Пропустити поточний пункт",
                            callback_data="skip_loading_type",
                        )
                    ],
                ]
            ),
        )
        return

    # Стандартна форма
    prompt = FIELD_PROMPTS.get(field, "Введіть значення:")
    await message.answer(
        prompt,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏭️ Пропустити поточний пункт",
                        callback_data=f"skip_{field}",
                    )
                ]
            ]
        ),
    )


async def go_to_next_step(state: FSMContext, current_step: str, message: Message):
    next_step_index = ALL_FIELDS.index(current_step) + 1
    if next_step_index >= len(ALL_FIELDS):
        from .summary import (
            show_summary,
        )  # імпортуємо тут, щоб уникнути циклічного імпорту

        await show_summary(message, state)
        return

    next_step = ALL_FIELDS[next_step_index]
    await ask_for_step(state, next_step, message)


async def go_to_next_edit_step(state: FSMContext, current_field: str, message: Message):
    data = await state.get_data()
    queue = data.get("edit_queue", [])
    if current_field in queue:
        queue.remove(current_field)
        await state.update_data(edit_queue=queue)

    if not queue:
        from .summary import show_summary

        await show_summary(message, state)
        return

    next_field = queue[0]
    await ask_for_step(state, next_field, message)


async def go_to_edit_step(state: FSMContext, field: str, message: Message):
    """
    Редагує лише одне поле (викликається з меню редагування).
    Після введення буде показано summary знову.
    """
    await ask_for_step(state, field, message)


async def safe_edit_text(
    message: Message | CallbackQuery, text: str, reply_markup=None
):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except Exception as e:
        if "message is not modified" not in str(e).lower():
            raise
