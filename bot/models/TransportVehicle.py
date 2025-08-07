from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.database import Base


class TransportVehicle(Base):
    __tablename__ = "transport_vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)

    vehicle_type: Mapped[str] = mapped_column(String(100))  # Тип ТЗ (фура, тягач тощо)
    registration_number: Mapped[str] = mapped_column(String(100))  # Номер(и) авто
    load_capacity_tons: Mapped[str] = mapped_column(
        String(20)
    )  # Вантажопідйомність (наприклад: 23 т)
    body_volume_m3: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # Обʼєм (наприклад: 86 м3)
    special_equipment: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Завантаження: "Бік, Зад"

    driver_fullname: Mapped[str] = mapped_column(String(100), nullable=True)
    driver_phone: Mapped[str] = mapped_column(String(20), nullable=True)

    carrier_company_id: Mapped[int] = mapped_column(
        ForeignKey("carrier_companies.id", ondelete="CASCADE")
    )
    carrier_company = relationship("CarrierCompany", back_populates="vehicles")
