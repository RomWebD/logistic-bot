"""
Форма реєстрації клієнта з використанням сервісів
"""

from bot.forms.base import BaseForm, FormField
from bot.services.client.registration import ClientRegistrationService
from bot.schemas.client import ClientRegistrationData
from bot.utils.validators import (
    validate_phone_field,
    normalize_phone_field,
    validate_email,
    validate_tax_id,
)
from aiogram.types import Message
from bot.ui.keyboards import client_main_kb as get_client_main_menu


class ClientRegistrationForm(BaseForm):
    """
    Форма реєстрації клієнта
    Вся логіка валідації винесена в окремі функції
    """

    summary_header = "🧑‍💼 <b>Реєстрація клієнта:</b>"
    include_progress = True

    fields = [
        FormField(
            name="full_name",
            title="ПІБ",
            kind="text",
            prompt="👤 Введіть ваше ПІБ:",
            validator=lambda v: None if len(v) >= 3 else "ПІБ занадто коротке",
            allow_skip=False,
        ),
        FormField(
            name="phone",
            title="Телефон",
            kind="text",
            prompt="📞 Введіть номер телефону:",
            validator=lambda v: validate_phone_field(v, "UA"),
            normalizer=lambda v: normalize_phone_field(v, "UA"),
            allow_skip=False,
        ),
        FormField(
            name="email",
            title="Email",
            kind="text",
            prompt="📧 Введіть email:",
            validator=validate_email,
            normalizer=lambda v: v.lower().strip(),
            allow_skip=False,
        ),
        FormField(
            name="company_name",
            title="Компанія",
            kind="text",
            prompt="🏢 Назва компанії:",
            allow_skip=False,
        ),
        FormField(
            name="tax_id",
            title="ЄДРПОУ/ІПН",
            kind="text",
            prompt="🆔 ЄДРПОУ (8 цифр) або ІПН (10 цифр):",
            validator=validate_tax_id,
            normalizer=lambda v: "".join(filter(str.isdigit, v)),
            allow_skip=False,
        ),
        FormField(
            name="address",
            title="Адреса",
            kind="text",
            prompt="📍 Адреса офісу:",
            allow_skip=False,
        ),
        FormField(
            name="website",
            title="Сайт",
            kind="text",
            prompt="🌐 Сайт компанії (або пропустіть):",
            allow_skip=True,
        ),
    ]

    icons = {
        "full_name": "👤",
        "phone": "📞",
        "email": "📧",
        "company_name": "🏢",
        "tax_id": "🆔",
        "address": "📍",
        "website": "🌐",
    }

    async def on_submit(self, data: dict, message: Message):
        """
        Обробка сабміту форми через сервіс
        """
        # Отримуємо telegram_id зі state
        telegram_id = data.get("tg_id")
        if not telegram_id:
            await message.answer("❌ Помилка: відсутній telegram_id")
            return

        # Створюємо DTO
        try:
            registration_data = ClientRegistrationData(
                telegram_id=telegram_id,
                full_name=data["full_name"],
                phone=data["phone"],
                email=data["email"],
                company_name=data["company_name"],
                tax_id=data["tax_id"],
                address=data["address"],
                website=data.get("website"),
            )
        except Exception as e:
            await message.answer(f"❌ Помилка валідації: {e}")
            return

        # Використовуємо сервіс
        async with ClientRegistrationService() as service:
            result = await service.register(registration_data)

        # Обробляємо результат
        if result["success"]:
            await message.answer(
                "✅ Реєстрація успішна!\n⏳ Очікуйте верифікації адміністратором.",
                reply_markup=get_client_main_menu(is_verified=False),
            )
        else:
            error_messages = {
                "CLIENT_EXISTS": "Ви вже зареєстровані",
                "EMAIL_EXISTS": "Email вже використовується",
                "REGISTRATION_ERROR": "Технічна помилка, спробуйте пізніше",
            }
            msg = error_messages.get(
                result.get("code"), result.get("message", "Невідома помилка")
            )
            await message.answer(f"❌ {msg}")
