from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()


class RegisterCar(StatesGroup):
    car_type = State()
    plate_number = State()
    weight_capacity = State()
    volume = State()
    loading_type = State()
    driver_fullname = State()
    driver_phone = State()


ALL_FIELDS = [
    "car_type",
    "plate_number",
    "weight_capacity",
    "volume",
    "loading_type",
    "driver_fullname",
    "driver_phone",
]


def get_progress_bar(state_data: dict) -> str:
    filled = sum(1 for field in ALL_FIELDS if state_data.get(field))
    percent = int((filled / len(ALL_FIELDS)) * 100)
    blocks = int(percent / 10)
    return f"\n\n📊 Прогрес: [{'■' * blocks}{'□' * (10 - blocks)}] {percent}%"


async def go_to_next_step(state: FSMContext, current_step: str, message: Message):
    next_step_index = ALL_FIELDS.index(current_step) + 1
    if next_step_index >= len(ALL_FIELDS):
        await show_summary(message, state)
        return

    next_step = ALL_FIELDS[next_step_index]
    await state.set_state(getattr(RegisterCar, next_step))

    # 🟨 Спеціальна логіка для loading_type
    if next_step == "loading_type":
        await state.update_data(loading_type=set())  # ініціалізуємо пусту множину
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

    # 🟩 Звичайні поля
    prompts = {
        "plate_number": "Введіть номер(и) авто (наприклад: АС2369СА / АС5729ХР):",
        "weight_capacity": "Введіть вантажопідйомність (наприклад: 23 тони):",
        "volume": "Введіть обʼєм (наприклад: 86 м3):",
        "driver_fullname": "Введіть ПІБ водія:",
        "driver_phone": "Введіть номер телефону водія:",
    }

    prompt_text = prompts.get(next_step, "Введіть значення:")
    await message.answer(
        prompt_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏭️ Пропустити поточний пункт",
                        callback_data=f"skip_{next_step}",
                    )
                ]
            ]
        ),
    )


@router.callback_query(F.data.startswith("skip_"))
async def skip_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.replace("skip_", "")
    await state.update_data({field: None})
    await go_to_next_step(state, field, callback.message)


async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    summary = (
        f"🚚 **Перевірте введені дані:**\n"
        f"Тип: {data.get('car_type') or '-'}\n"
        f"Номер(и): {data.get('plate_number') or '-'}\n"
        f"Вантажопідйомність: {data.get('weight_capacity') or '-'}\n"
        f"Обʼєм: {data.get('volume') or '-'}\n"
        f"Завантаження: {', '.join(data.get('loading_type', []) or [])}\n"
        f"Водій: {data.get('driver_fullname') or '-'}\n"
        f"Телефон: {data.get('driver_phone') or '-'}\n"
    ) + get_progress_bar(data)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Зберегти", callback_data="car_save"),
                InlineKeyboardButton(text="✏️ Редагувати", callback_data="car_edit"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="car_back")],
        ]
    )

    await message.answer(summary, reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data == "carrier_add_new_car")
async def start_register_car(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🚛 Оберіть тип транспорту:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Тент", callback_data="type_Tент"),
                    InlineKeyboardButton(
                        text="Рефрижератор", callback_data="type_Рефрижератор"
                    ),
                    InlineKeyboardButton(
                        text="Цистерна", callback_data="type_Цистерна"
                    ),
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
                        text="⏭️ Пропустити поточний пункт",
                        callback_data="skip_car_type",
                    ),
                ],
            ]
        ),
    )
    await state.set_state(RegisterCar.car_type)


@router.callback_query(RegisterCar.car_type, F.data.startswith("type_"))
async def set_vehicle_type(callback: CallbackQuery, state: FSMContext):
    value = callback.data.removeprefix("type_")
    if value == "other":
        await callback.message.answer("Введіть тип транспорту вручну:")
    else:
        await state.update_data(car_type=value)
        await go_to_next_step(state, "car_type", callback.message)


@router.message(RegisterCar.car_type)
async def set_custom_type(message: Message, state: FSMContext):
    await state.update_data(car_type=message.text)
    await go_to_next_step(state, "car_type", message)


@router.message(RegisterCar.plate_number)
async def set_plate(message: Message, state: FSMContext):
    await state.update_data(plate_number=message.text)
    await go_to_next_step(state, "plate_number", message)


@router.message(RegisterCar.weight_capacity)
async def set_capacity(message: Message, state: FSMContext):
    await state.update_data(weight_capacity=message.text)
    await go_to_next_step(state, "weight_capacity", message)


@router.message(RegisterCar.volume)
async def set_volume(message: Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await go_to_next_step(state, "volume", message)


@router.callback_query(RegisterCar.loading_type)
async def choose_loading(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    loading: set = data.get("loading_type", set())

    option_map = {
        "load_side": "Бік",
        "load_top": "Верх",
        "load_back": "Зад",
    }

    if callback.data == "load_done":
        await state.update_data(loading_type=list(loading))
        await go_to_next_step(state, "loading_type", callback.message)
        return

    if callback.data in option_map:
        option = option_map[callback.data]
        if option in loading:
            loading.remove(option)
        else:
            loading.add(option)

        await state.update_data(loading_type=loading)

        # ✅ Динамічний текст + markup
        selected_text = (
            f"Оберіть спосіб завантаження:\nВибрано: {', '.join(loading) or 'нічого'}"
        )
        await callback.message.edit_text(
            selected_text,
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


# @router.callback_query(RegisterCar.loading_type)
# async def choose_loading(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     loading: set = data.get("loading_type", set())

#     if callback.data == "load_done":
#         await state.update_data(loading_type=list(loading))
#         await go_to_next_step(state, "loading_type", callback.message)
#         return

#     option_map = {
#         "load_side": "Бік",
#         "load_top": "Верх",
#         "load_back": "Зад",
#     }

#     option = option_map.get(callback.data)
#     if option in loading:
#         loading.remove(option)
#     else:
#         loading.add(option)

#     await state.update_data(loading_type=loading)
#     await callback.answer(f"Вибрано: {', '.join(loading)}")


@router.message(RegisterCar.driver_fullname)
async def set_driver_name(message: Message, state: FSMContext):
    await state.update_data(driver_fullname=message.text)
    await go_to_next_step(state, "driver_fullname", message)


@router.message(RegisterCar.driver_phone)
async def finish_registration(message: Message, state: FSMContext):
    await state.update_data(driver_phone=message.text)
    await go_to_next_step(state, "driver_phone", message)


@router.callback_query(F.data == "car_save")
async def save_car(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text("✅ Транспорт успішно додано!", reply_markup=None)
    await state.clear()


@router.callback_query(F.data == "car_edit")
async def edit_car(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔁 Оберіть поле, яке бажаєте змінити:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🚛 Тип транспорту", callback_data="edit_car_type"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔢 Номер(и) авто", callback_data="edit_plate_number"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⚖️ Вантажопідйомність",
                        callback_data="edit_weight_capacity",
                    )
                ],
                [InlineKeyboardButton(text="📦 Обʼєм", callback_data="edit_volume")],
                [
                    InlineKeyboardButton(
                        text="📥 Спосіб завантаження", callback_data="edit_loading_type"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👤 ПІБ водія", callback_data="edit_driver_fullname"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📞 Телефон водія", callback_data="edit_driver_phone"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Завершити редагування", callback_data="edit_done"
                    )
                ],
            ]
        ),
    )


@router.callback_query(F.data == "car_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⬅️ Введіть номер телефону водія ще раз:")
    await state.set_state(RegisterCar.driver_phone)
