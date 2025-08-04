from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    MenuButtonCommands,
)
from bot.database.database import async_session
from sqlalchemy import select
from bot.models.carrier_company import CarrierCompany


async def set_verified_carrier_menu(bot: Bot, chat_id: int):
    commands = [
        BotCommand(command="menu", description="📋 Меню перевізника"),
        BotCommand(command="start", description="🔄 Почати / перезапустити"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=chat_id))
    await bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButtonCommands())


# async def remove_menu_for_all(bot: Bot):
#     await bot.delete_my_commands(scope=BotCommandScopeDefault())
#     await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
async def remove_menu_for_all(bot: Bot):
    async with async_session() as session:
        result = await session.scalars(
            select(CarrierCompany.telegram_id)
            # .where(CarrierCompany.is_verify == False)
        )
        ids = result.all()

    for user_id in ids:
        try:
            await bot.set_my_commands([], scope=BotCommandScopeChat(chat_id=user_id))
        except Exception as e:
            print(f"❌ Не вдалося видалити меню для {user_id}: {e}")
