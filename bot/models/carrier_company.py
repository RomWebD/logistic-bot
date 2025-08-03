# bot/models/carrier_company.py

from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.database import Base


class CarrierCompany(Base):
    __tablename__ = "carrier_companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger(), nullable=False, unique=True, index=True, comment="Telegram ID користувача"
    )
    is_verify: Mapped[bool] = mapped_column(Boolean(), default=False)

    # 📌 Контактна інформація
    contact_full_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="ПІБ контактної особи"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Мобільний телефон"
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Електронна пошта"
    )

    # 🏢 Компанія
    company_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Назва компанії або ФОП"
    )
    ownership_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Форма власності (ТОВ, ФОП тощо)"
    )
    tax_id: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="ЄДРПОУ / ІПН"
    )
    office_address: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Адреса офісу (місто, вулиця, індекс)"
    )
    website: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="Посилання на веб‑сайт (необов’язково)"
    )
