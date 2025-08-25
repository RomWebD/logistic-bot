"""
⏰ БАЗОВІ MIXINS - timestamps та інше
"""
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import DateTime, func, Integer
from datetime import datetime


class TimestampMixin:
    """
    Часові мітки для відстеження змін
    
    Чому окремий mixin:
    - DRY принцип - не повторюємо в кожній моделі
    - Consistency - всюди однакові назви полів
    - Maintainability - змінюємо в одному місці
    """
    
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True), 
            server_default=func.now(),
            nullable=False,
            comment="Час створення запису"
        )
    
    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True), 
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
            comment="Час останнього оновлення"
        )


class SoftDeleteMixin:
    """
    М'яке видалення - запис не видаляється, а помічається як видалений
    
    Переваги:
    - Можна відновити випадково видалені дані
    - Зберігається історія
    - Безпечніше для бізнесу
    """
    
    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=True,
            comment="Час видалення (NULL = не видалено)"
        )
    
    @property
    def is_deleted(self) -> bool:
        """Чи видалений запис"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Помітити як видалений"""
        self.deleted_at = datetime.now()
    
    def restore(self) -> None:
        """Відновити видалений запис"""
        self.deleted_at = None