from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.forms.aiogram_adapter import FormRouter
from bot.forms.client_registration import ClientRegistrationForm

# Створюємо форму та її роутер
client_registration_form = ClientRegistrationForm()
client_form_router = FormRouter(client_registration_form, prefix="client")


async def start_registration_flow(message: Message, state: FSMContext):
    """
    Запускає FSM-реєстрацію клієнта без додаткових кнопок.
    """
    await state.update_data(tg_id=message.from_user.id)
    await client_registration_form.start(message, state)
