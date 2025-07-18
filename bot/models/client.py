from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from bot.database.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    full_name: Mapped[str]
    phone: Mapped[str]
