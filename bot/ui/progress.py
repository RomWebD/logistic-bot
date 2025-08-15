from typing import Any, List, Type
from aiogram.fsm.state import StatesGroup, State


def _state_names(group: Type[StatesGroup]) -> List[str]:
    # збираємо всі атрибути класу, що є State
    return [name for name, val in group.__dict__.items() if isinstance(val, State)]


def _is_filled(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        s = v.strip()
        return bool(s) and s != "-"  # порожнє/«-» не рахуємо
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) > 0
    return True


def _bar(filled: int, total: int, scale: int = 10) -> str:
    if total <= 0:
        return "[{}] 0% (0/0)".format("□" * scale)
    pct = int((filled / total) * 100)
    blocks = min(scale, max(0, int(round(pct * scale / 100))))
    return "[{}{}] {}% ({}/{})".format(
        "■" * blocks, "□" * (scale - blocks), pct, filled, total
    )


def progress_text(state_data: dict, group: Type[StatesGroup]) -> str:
    """
    Прогрес рахується за ІМЕНАМИ стейтів у StatesGroup.
    Ніяких додаткових параметрів.
    """
    fields = _state_names(group)
    total = len(fields)
    filled = sum(1 for f in fields if _is_filled(state_data.get(f)))
    return f"\n\n📊 Прогрес: {_bar(filled, total)}"
