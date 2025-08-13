# bot/database/models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, Boolean, text
from bot.database.database import Base



class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    is_verify: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    company_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # опційно: created_at/updated_at — якщо у вас є міксін
