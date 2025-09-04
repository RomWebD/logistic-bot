# bot/forms/carrier_registration.py
from aiogram.types import Message
from bot.forms.base import BaseForm, FormField
from bot.schemas.carrier import CarrierRegistrationData
from bot.services.carrier.registration import CarrierRegistrationService
from bot.utils.validators import (
    validate_phone_field, normalize_phone_field,
    validate_email, validate_tax_id,
)

class CarrierRegistrationForm(BaseForm):
    summary_header = "🚚 <b>Реєстрація перевізника:</b>"
    include_progress = True

    fields = [
        FormField(
            name="contact_full_name",
            title="Контактна особа",
            kind="text",
            prompt="👤 Введіть ПІБ контактної особи:<code>Іван Іванович</code>",
            validator=lambda v: None if len(v) >= 3 else "ПІБ занадто коротке",
            allow_skip=False,
        ),
        FormField(
            name="company_name",
            title="Компанія / ФОП",
            kind="text",
            prompt="🏢 Назва компанії або ФОП:<code>ТОВ Інтертрейд</code>",
            allow_skip=False,
        ),
        FormField(
            name="tax_id",
            title="ЄДРПОУ/ІПН",
            kind="text",
            prompt="🆔 ЄДРПОУ (8) або ІПН (10):<code>12345678</code>",
            validator=validate_tax_id,
            normalizer=lambda v: "".join(filter(str.isdigit, v)),
            allow_skip=False,
        ),
        FormField(
            name="phone",
            title="Телефон",
            kind="text",
            prompt="📞 Номер телефону:<code>0689384811</code>",
            validator=lambda v: validate_phone_field(v, "UA"),
            normalizer=lambda v: normalize_phone_field(v, "UA"),
            allow_skip=False,
        ),
        FormField(
            name="email",
            title="Email",
            kind="text",
            prompt="📧 Введіть email:<code>company@example.com</code>",
            validator=validate_email,
            normalizer=lambda v: v.lower().strip(),
            allow_skip=False,
        ),
        FormField(
            name="office_address",
            title="Адреса офісу",
            kind="text",
            prompt="📍 Адреса офісу:<code>Київ, вул. ...</code>",
            allow_skip=False,
        ),
        FormField(
            name="website",
            title="Сайт",
            kind="text",
            prompt="🌐 Сайт компанії (можна пропустити):<code>https://...</code>",
            allow_skip=True,
        ),
    ]

    icons = {
        "contact_full_name": "👤",
        "company_name": "🏢",
        "tax_id": "🆔",
        "phone": "📞",
        "email": "📧",
        "office_address": "📍",
        "website": "🌐",
    }

    async def on_submit(self, data: dict, message: Message):
        telegram_id = data.get("tg_id")
        if not telegram_id:
            await message.answer("❌ Помилка: відсутній telegram_id")
            return

        try:
            dto = CarrierRegistrationData(
                telegram_id=telegram_id,
                contact_full_name=data["contact_full_name"],
                company_name=data["company_name"],
                tax_id=data["tax_id"],
                phone=data["phone"],
                email=data["email"],
                office_address=data["office_address"],
                website=data.get("website"),
            )
        except Exception as e:
            await message.answer(f"❌ Помилка валідації: {e}")
            return

        async with CarrierRegistrationService() as svc:
            # додатковий «запор» від дублю (обхід кнопок)
            if await svc.get_by_tg(telegram_id):
                await message.answer("✅ Ви вже зареєстровані як перевізник.")
                return

            result = await svc.register(dto)

        if result["success"]:
            await message.answer(
                "✅ Реєстрація успішна!\n⏳ Очікуйте верифікації адміністратором."
            )
        else:
            errors = {
                "CARRIER_EXISTS": "Ви вже зареєстровані як перевізник",
                "REGISTRATION_ERROR": "Технічна помилка, спробуйте пізніше",
            }
            msg = errors.get(result.get("code"), result.get("message", "Невідома помилка"))
            await message.answer(f"❌ {msg}")
