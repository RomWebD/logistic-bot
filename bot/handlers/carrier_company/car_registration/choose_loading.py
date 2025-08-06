from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from .fsm import RegisterCar
from .fsm_helpers import go_to_next_step
from .edit import handle_editing_step

router = Router()


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
        # 🔍 редагування чи звичайна реєстрація?
        if "edit_queue" in data:
            await handle_editing_step(
                state, "loading_type", list(loading), callback.message
            )
        else:
            await state.update_data(loading_type=list(loading))
            await go_to_next_step(state, "loading_type", callback.message)

        await callback.answer()
        return

    if callback.data in option_map:
        option = option_map[callback.data]
        if option in loading:
            loading.remove(option)
        else:
            loading.add(option)
        await state.update_data(loading_type=loading)

        await callback.message.edit_text(
            f"Оберіть спосіб завантаження:\nВибрано: {', '.join(loading) or 'нічого'}",
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
