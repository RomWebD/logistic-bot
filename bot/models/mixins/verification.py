"""
✅ ВЕРИФІКАЦІЯ - теж окремо!
"""
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import Boolean, DateTime, Integer, String
from typing import Optional
from datetime import datetime


class VerificationMixin:
    """
    Верифікація користувачів/компаній
    
    Патерн: Audit Trail
    - Зберігаємо хто і коли верифікував
    - Можливість відкликати верифікацію
    """
    
    @declared_attr
    def is_verified(cls) -> Mapped[bool]:
        return mapped_column(
            Boolean,
            default=False,
            nullable=False,
            index=True,  # Індекс для фільтрації
            comment="Статус верифікації"
        )
    
    @declared_attr
    def verified_at(cls) -> Mapped[Optional[datetime]]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=True,
            comment="Час верифікації"
        )
    
    @declared_attr
    def verified_by_admin_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(
            Integer,
            nullable=True,
            comment="ID адміністратора який верифікував"
        )
    
    @declared_attr
    def verification_comment(cls) -> Mapped[Optional[str]]:
        return mapped_column(
            String(500),
            nullable=True,
            comment="Коментар адміністратора"
        )
    
    def verify(self, admin_id: int, comment: Optional[str] = None) -> None:
        """Метод верифікації"""
        self.is_verified = True
        self.verified_at = datetime.now()
        self.verified_by_admin_id = admin_id
        self.verification_comment = comment
    
    def revoke_verification(self, reason: str) -> None:
        """Відкликати верифікацію"""
        self.is_verified = False
        self.verification_comment = f"Відкликано: {reason}"