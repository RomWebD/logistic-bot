from datetime import datetime, timezone
from typing import Literal, Optional


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_google_time(ts: Optional[str]) -> Optional[datetime]:
    """
    Google Drive повертає RFC3339 із 'Z' наприкінці.
    Перетворимо на aware datetime (UTC). Якщо None або кривий формат — повернемо None.
    """
    if not ts:
        return None
    try:
        # 2025-08-18T15:34:56.000Z -> replace Z
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except Exception:
        return None
