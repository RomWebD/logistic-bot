from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Tuple
from aiogram.types import Message


@dataclass
class FormField:
    name: str
    title: str
    kind: str = "text"  # text | select | multiselect
    prompt: Optional[str] = None
    options: Optional[Sequence[Tuple[str, str]]] = None  # (value, label)
    allow_skip: bool = True
    # трансформер: вхідне повідомлення -> нормалізоване значення
    normalizer: Optional[Callable[[str], Any]] = None
    # валідація: значення -> помилка або None
    validator: Optional[Callable[[Any], Optional[str]]] = None


class BaseForm:
    """
    Контейнер бізнес-логіки форми (поля, порядок, summary, on_submit).
    Переноситься між FSM-кейсами: авто, клієнт, заявка, компанія і т.д.
    """

    # порядок полів
    fields: List[FormField] = []

    # заголовок у summary
    summary_header: str = "📄 <b>Підсумок</b>"

    # якщо True — показуємо прогресбар
    include_progress: bool = True

    # map[field_name] = icon (для summary)
    icons: Dict[str, str] = {}

    async def on_submit(
        self, data: Dict[str, Any], message: Message
    ) -> Awaitable[None]:
        """
        Перевизнач у конкретній формі — що робити при збереженні.
        Напр., збереження у БД + Celery-таски.
        """
        raise NotImplementedError

    # --------------- допоміжне ---------------

    def field_by_name(self, name: str) -> Optional[FormField]:
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def field_titles(self) -> Dict[str, str]:
        return {f.name: f.title for f in self.fields}
