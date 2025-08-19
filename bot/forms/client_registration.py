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
            prompt="👤 Введіть ваше ПІБ:",
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
            prompt="📧 Введіть вашу електронну пошту:",
            validator=lambda v: validate_email_input(v)[1],
        ),
        FormField(
            name="company_name",
            title="Компанія",
            kind="text",
            prompt="🏢 Введіть назву компанії:",
            validator=lambda v: validate_company_name_input(v)[1],
        ),
        FormField(
            name="tax_id",
            title="ЄДРПОУ / ІПН",
            kind="text",
            prompt="🆔 Введіть ЄДРПОУ (8 цифр) або ІПН (10 цифр):",
            validator=lambda v: validate_tax_id_input(v)[1],
        ),
        FormField(
            name="address",
            title="Адреса",
            kind="text",
            prompt="📍 Введіть адресу офісу (можна скорочено):",
            validator=_not_empty,
        ),
        FormField(
            name="website",
            title="Сайт",
            kind="text",
            prompt="🔗 Введіть сайт компанії або '-' якщо немає:",
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

    async def on_submit(self, data: Dict[str, Any]):
        telegram_id = data.get("tg_id")
        if telegram_id is None:
            raise RuntimeError("tg_id is required in state data for ClientRegistrationForm")

        # Перевірка чи вже є клієнт
        if await check_existing_client(telegram_id):
            return "⚠️ Ви вже зареєстровані як клієнт."

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
            return "⚠️ Клієнт з таким номером або поштою вже існує."

        return (
            "✅ Реєстрація клієнта успішна!\n"
            "⚠️ Ви ще не верифіковані. Зачекайте підтвердження."
        )
