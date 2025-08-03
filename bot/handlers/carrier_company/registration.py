from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from bot.models.carrier_company import CarrierCompany
from bot.database.database import async_session
from bot.services.bot_commands import set_verified_carrier_menu

router = Router()


class RegisterCarrierCompany(StatesGroup):
    contact_full_name = State()
    company_name = State()
    ownership_type = State()
    tax_id = State()
    phone = State()
    email = State()
    office_address = State()
    website = State()


@router.callback_query(F.data == "role_carrier")
async def handle_role_carrier(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "👋 Розпочнемо реєстрацію компанії-перевізника.\n\nВведіть ПІБ контактної особи:"
    )
    await state.set_state(RegisterCarrierCompany.contact_full_name)
    await callback.answer()


@router.message(RegisterCarrierCompany.contact_full_name)
async def get_contact_full_name(message: Message, state: FSMContext):
    await state.update_data(contact_full_name=message.text)
    await message.answer("🏢 Введіть назву компанії або ФОП:")
    await state.set_state(RegisterCarrierCompany.company_name)


@router.message(RegisterCarrierCompany.company_name)
async def get_company_name(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer("📄 Введіть форму власності (ТОВ, ФОП, інше):")
    await state.set_state(RegisterCarrierCompany.ownership_type)


@router.message(RegisterCarrierCompany.ownership_type)
async def get_ownership_type(message: Message, state: FSMContext):
    await state.update_data(ownership_type=message.text)
    await message.answer("🆔 Введіть ЄДРПОУ / ІПН:")
    await state.set_state(RegisterCarrierCompany.tax_id)


@router.message(RegisterCarrierCompany.tax_id)
async def get_tax_id(message: Message, state: FSMContext):
    await state.update_data(tax_id=message.text)
    await message.answer("📱 Введіть номер телефону:")
    await state.set_state(RegisterCarrierCompany.phone)


@router.message(RegisterCarrierCompany.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("📧 Введіть електронну пошту:")
    await state.set_state(RegisterCarrierCompany.email)


@router.message(RegisterCarrierCompany.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("📍 Введіть адресу офісу (місто, вулиця, індекс):")
    await state.set_state(RegisterCarrierCompany.office_address)


@router.message(RegisterCarrierCompany.office_address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(office_address=message.text)
    await message.answer("🔗 Посилання на вебсайт (або - якщо немає):")
    await state.set_state(RegisterCarrierCompany.website)


@router.message(RegisterCarrierCompany.website)
async def finish_company_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id

    async with async_session() as session:
        existing = await session.scalar(
            select(CarrierCompany).where(CarrierCompany.phone == data["phone"])
        )
        if existing:
            await message.answer("🔁 Компанія з таким номером вже зареєстрована.")
        else:
            session.add(
                CarrierCompany(
                    telegram_id=telegram_id,
                    contact_full_name=data["contact_full_name"],
                    company_name=data["company_name"],
                    ownership_type=data["ownership_type"],
                    tax_id=data["tax_id"],
                    phone=data["phone"],
                    email=data["email"],
                    office_address=data["office_address"],
                    website=None if message.text.strip() == "-" else message.text,
                )
            )
            await session.commit()

            from bot.services.loader import bot

            await set_verified_carrier_menu(bot, telegram_id)

            # commands = [
            #     BotCommand(command="menu", description="📋 Меню перевізника"),
            #     BotCommand(command="start", description="🔄 Почати / перезапустити"),
            # ]
            # await bot.set_my_commands(
            #     commands, scope=BotCommandScopeChat(chat_id=telegram_id)
            # )
            # await bot.set_chat_menu_button(
            #     chat_id=telegram_id, menu_button=MenuButtonCommands()
            # )
            await message.answer(
                "✅ Реєстрація компанії успішна!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="➕ Додати водія", callback_data="add_driver"
                            )
                        ]
                    ]
                ),
            )
    await state.clear()
