# bot/forms/client_registration.py
from __future__ import annotations
from typing import Any, Dict
from dataclasses import dataclass

from bot.forms.base import BaseForm, FormField
from bot.services.client.client_registration import (
    check_existing_client,
    register_new_client,
)
from bot.schemas.client import (
    ClientRegistrationData,
    validate_full_name_input,
    validate_phone_input,
    validate_email_input,
    validate_company_name_input,
    validate_tax_id_input,
    validate_website_input,
)
from aiogram.types import Message

from bot.ui.keyboards import client_main_kb


def _not_empty(v: Any) -> str | None:
    if not v or (isinstance(v, str) and not v.strip()):
        return "Поле не може бути порожнім"
    return None


class ClientRegistrationForm(BaseForm):
    summary_header = "🧑‍💼 <b>Реєстрація клієнта:</b>"
    include_progress = True

    fields = [
        FormField(
            name="full_name",
            title="ПІБ",
            kind="text",
            prompt="👤 Введіть ваше ПІБ (приклад: <code>Петро Василишин</code>):",
            validator=lambda v: validate_full_name_input(v)[1],
        ),
        FormField(
            name="phone",
            title="Телефон",
            kind="text",
            prompt="📞 Введіть ваш номер телефону (напр.: <code>+380501234567</code>):",
            validator=lambda v: validate_phone_input(v)[1],
        ),
        FormField(
            name="email",
            title="Email",
            kind="text",
            prompt="📧 Введіть вашу електронну пошту (напр.: <code>name@example.com</code>):",
            validator=lambda v: validate_email_input(v)[1],
        ),
        FormField(
            name="company_name",
            title="Компанія",
            kind="text",
            prompt="🏢 Введіть назву компанії (приклад: <code>ТОВ Кронтехно</code> або <code>ФОП Петришин Петро</code>):",
            validator=lambda v: validate_company_name_input(v)[1],
        ),
        FormField(
            name="tax_id",
            title="ЄДРПОУ / ІПН",
            kind="text",
            prompt="🆔 Введіть ЄДРПОУ (8 цифр) або ІПН (10 цифр) (приклад: <code>12345678</code>):",
            validator=lambda v: validate_tax_id_input(v)[1],
        ),
        FormField(
            name="address",
            title="Адреса",
            kind="text",
            prompt="📍 Введіть адресу офісу (приклад: <code>Івано-Франківськ</code>):",
            validator=_not_empty,
        ),
        FormField(
            name="website",
            title="Сайт",
            kind="text",
            prompt="🔗 Введіть сайт компанії або '-' якщо немає (приклад: <code>https://google.com</code>):",
            validator=lambda v: validate_website_input(v)[1],
        ),
    ]
    icons = {
        "full_name": "👤",
        "phone": "📞",
        "email": "📧",
        "company_name": "🏢",
        "tax_id": "🆔",
        "address": "📍",
        "website": "🔗",
    }


    async def on_submit(self, data: dict, message: Message):
        telegram_id = data.get("tg_id")
        if not telegram_id:
            await message.answer("❌ Помилка: відсутній telegram_id")
            return

        if await check_existing_client(telegram_id):
            await message.answer("⚠️ Ви вже зареєстровані як клієнт.")
            return

        payload = ClientRegistrationData(
            telegram_id=telegram_id,
            full_name=data["full_name"],
            phone=data["phone"],
            email=data["email"],
            company_name=data["company_name"],
            tax_id=data["tax_id"],
            address=data["address"],
            website=None if data["website"] == "-" else data["website"],
        )

        success = await register_new_client(payload)
        if not success:
            await message.answer("⚠️ Клієнт з таким номером або поштою вже існує.")
            return

        # ✨ Оновлення summary (опційно)
        try:
            await message.edit_text(
                self.build_summary(data, include_progress=False),
                parse_mode="HTML"
            )
        except Exception:
            pass

        # Надсилаємо головне меню
        await message.answer(
            "✅ Реєстрація клієнта успішна!\n"
            "⚠️ Ви ще не верифіковані. Зачекайте підтвердження або зверніться до адміністратора.",
            reply_markup=client_main_kb(is_verified=False),
        )