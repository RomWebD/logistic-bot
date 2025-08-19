# bot/ui/summary.py
from __future__ import annotations
from typing import Any, Type, Mapping, Optional, List, Tuple
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from html import escape as _esc
from urllib.parse import urlparse

# ---------- helpers ----------


def _state_names(group: Type[StatesGroup]) -> list[str]:
    return [name for name, val in group.__dict__.items() if isinstance(val, State)]


def _is_filled(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip()) and v.strip() != "-"
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) > 0
    return True


def _looks_like_url(s: str) -> bool:
    try:
        p = urlparse(s.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _looks_like_phone(s: str) -> bool:
    s = s.strip()
    if s.startswith("+"):
        digits = "".join(ch for ch in s[1:] if ch.isdigit())
        return len(digits) >= 7
    return False


# Іконки для полів
ICON_PRESET: dict[str, str] = {
    "full_name": "🧑‍💼",
    "contact_full_name": "🧑‍💼",
    "driver_fullname": "🧑‍✈️",
    "phone": "📱",
    "driver_phone": "📞",
    "email": "✉️",
    "company_name": "🏢",
    "tax_id": "🆔",
    "edrpou": "🆔",
    "ipn": "🆔",
    "office_address": "📍",
    "address": "📍",
    "website": "🔗",
    "car_type": "🚚",
    "plate_number": "🚘",
    "weight_capacity": "⚖️",
    "volume": "📦",
    "loading_type": "🪝",
}


def _icon_for(field: str, titles: Mapping[str, str]) -> str:
    f = field.lower()
    if f in ICON_PRESET:
        return ICON_PRESET[f]
    t = titles.get(field, field).lower()
    for key, emoji in ICON_PRESET.items():
        if key in t:
            return emoji
    return "•"


def _value_for_pre(field: str, v: Any) -> str:
    """Рендер значення для <pre> з клікабельними URL/телефонами"""
    if not _is_filled(v):
        return "-"
    s = str(v).strip()
    if _looks_like_url(s):
        return f'<a href="{_esc(s, quote=True)}">{_esc(s)}</a>'
    if _looks_like_phone(s):
        tel = "+" + "".join(ch for ch in s if ch.isdigit())
        return f'<a href="tel:{_esc(tel, quote=True)}">{_esc(s)}</a>'
    return _esc(s)


def _progress_numbers(
    state_data: Mapping[str, Any], group: Type[StatesGroup]
) -> Tuple[int, int, int]:
    fields = _state_names(group)
    total = len(fields)
    filled = sum(1 for f in fields if _is_filled(state_data.get(f)))
    pct = int((filled / total) * 100) if total else 0
    return filled, total, pct


def _progress_bar_blocks(pct: int, total_blocks: int = 20) -> str:
    """Сучасний прогрес-бар у вигляді блоків █ і ░"""
    filled_blocks = round(total_blocks * pct / 100)
    empty_blocks = total_blocks - filled_blocks
    return f"[{'█' * filled_blocks}{'░' * empty_blocks}] {pct}%"


# ---------- PUBLIC API ----------


def build_summary_text(
    state_data: Mapping[str, Any],
    group: Type[StatesGroup],
    titles: Mapping[str, str],
    *,
    include_progress: bool = True,
    hide_empty: bool = False,
    header: Optional[str] = "ПІДСУМОК",
) -> str:
    fields = _state_names(group)
    visible_fields = [
        f for f in fields if not (hide_empty and not _is_filled(state_data.get(f)))
    ]

    # --- Форма ---
    form_lines: List[str] = []
    for f in visible_fields:
        icon = _icon_for(f, titles)
        label = titles.get(f, f)
        value = _value_for_pre(f, state_data.get(f))
        # без вирівнювання — просто одразу після двокрапки
        form_lines.append(f"{icon} {label}: {value}")

    # --- Заголовок та підказка ---
    if header:
        header_part = (
            "Перед збереженням, будь ласка, перевірте правильність введених даних.\n"
            "Якщо щось потрібно змінити — натисніть <b> ✏️Редагувати</b>.\n"
        )
    else:
        header_part = ""

    text = f"{header_part}<pre>{'\n'.join(form_lines)}</pre>"

    # --- Прогрес ---
    if include_progress:
        filled, total, pct = _progress_numbers(state_data, group)

        # вибір кольору
        if pct < 30:
            fill_emoji = "🟥"
        elif pct < 70:
            fill_emoji = "🟧"
        else:
            fill_emoji = "🟩"

        empty_emoji = "⬜"

        total_blocks = 10
        filled_blocks = round(total_blocks * pct / 100)
        empty_blocks = total_blocks - filled_blocks
        bar = (fill_emoji * filled_blocks) + (empty_emoji * empty_blocks)

        text += f"\n{bar} {pct}% ({filled}/{total})"

    return text


def build_summary_main_keyboard(
    edit_kb: str = "summary_edit",
    save_kb: str = "summary_confirm",
    cancel_kb: str = "summary_cancel",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редагувати", callback_data=edit_kb)],
            [InlineKeyboardButton(text="✅ Зберегти", callback_data=save_kb)],
            [InlineKeyboardButton(text="❌ Скасувати", callback_data=cancel_kb)],
        ]
    )


def build_edit_field_keyboard(
    group: Type[StatesGroup],
    titles: Mapping[str, str],
    *,
    edit_prefix: str = "edit_field",
    row_width: int = 2,
) -> InlineKeyboardMarkup:
    fields = _state_names(group)
    rows, row = [], []
    for f in fields:
        label = titles.get(f, f)
        row.append(InlineKeyboardButton(text=label, callback_data=f"{edit_prefix}:{f}"))
        if len(row) == row_width:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="summary_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def state_by_name(group: Type[StatesGroup], field_name: str) -> Optional[State]:
    st = getattr(group, field_name, None)
    return st if isinstance(st, State) else None
