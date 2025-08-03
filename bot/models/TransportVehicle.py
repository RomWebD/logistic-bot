from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.database import Base


class TransportVehicle(Base):
    __tablename__ = "transport_vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)

    vehicle_type: Mapped[str] = mapped_column(String(100))  # Тип ТЗ (фура, тягач тощо)
    brand_model_year: Mapped[str] = mapped_column(String(100))  # Марка / модель / рік
    registration_number: Mapped[str] = mapped_column(String(20), unique=True)  # Номер
    load_capacity_tons: Mapped[float] = mapped_column()  # Вантажопідйомність (тонн)
    body_volume_m3: Mapped[float] = mapped_column(nullable=True)  # Обʼєм кузова
    special_equipment: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Спецобладнання

    carrier_company_id: Mapped[int] = mapped_column(
        ForeignKey("carrier_companies.id", ondelete="CASCADE")
    )
    carrier_company = relationship("CarrierCompany", back_populates="vehicles")
