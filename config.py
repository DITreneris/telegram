"""Load env and paths. Validated at bot startup."""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CONTENT_PATH = BASE_DIR / "data" / "content.json"
STATE_PATH = BASE_DIR / "data" / "state.json"

_LOG_LEVEL_NAMES = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID: int | None = None

ENABLE_SCHEDULED_POSTING = False
SCHEDULE_TIMEZONE: ZoneInfo | None = None
SCHEDULE_TARGET_CHAT_ID: int | None = None
SCHEDULE_NOTIFY_ON_FAILURE = True


def resolve_log_level() -> int:
    """Grąžina logging lygį iš LOG_LEVEL (numatytai INFO). Netinkama reikšmė → INFO."""
    raw = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if not raw or raw not in _LOG_LEVEL_NAMES:
        if raw and raw not in _LOG_LEVEL_NAMES:
            warnings.warn(
                f'LOG_LEVEL "{os.getenv("LOG_LEVEL", "")!r}" neatpažintas; naudojamas INFO.',
                UserWarning,
                stacklevel=1,
            )
        return logging.INFO
    return int(getattr(logging, raw))


def _parse_env_bool(raw: str | None, default: bool) -> bool:
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def validate_config() -> None:
    global ADMIN_CHAT_ID, ENABLE_SCHEDULED_POSTING, SCHEDULE_NOTIFY_ON_FAILURE
    global SCHEDULE_TIMEZONE, SCHEDULE_TARGET_CHAT_ID
    if not BOT_TOKEN:
        raise ValueError("Nustatyk BOT_TOKEN aplinkos kintamąjį arba .env faile.")
    raw = os.getenv("ADMIN_CHAT_ID", "").strip()
    if not raw:
        raise ValueError(
            "Nustatyk ADMIN_CHAT_ID aplinkos kintamąjį arba .env faile "
            "(sveikasis skaičius, ne 0)."
        )
    try:
        aid = int(raw)
    except ValueError as exc:
        raise ValueError(
            "ADMIN_CHAT_ID turi būti sveikasis skaičius "
            "(pvz. Telegram naudotojo ar pokalbio id)."
        ) from exc
    if aid == 0:
        raise ValueError("ADMIN_CHAT_ID negali būti 0.")
    ADMIN_CHAT_ID = aid

    ENABLE_SCHEDULED_POSTING = _parse_env_bool(os.getenv("ENABLE_SCHEDULED_POSTING"), False)
    SCHEDULE_TIMEZONE = None
    SCHEDULE_TARGET_CHAT_ID = None

    if ENABLE_SCHEDULED_POSTING:
        tz_name = (os.getenv("SCHEDULE_TZ") or "Europe/Vilnius").strip() or "Europe/Vilnius"
        try:
            SCHEDULE_TIMEZONE = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(
                f'Naudojamas nežinomas SCHEDULE_TZ: {tz_name!r} (IANA laiko juosta, pvz. "Europe/Vilnius").'
            ) from exc

        raw_target = (os.getenv("SCHEDULE_TARGET_CHAT_ID") or "").strip()
        if not raw_target:
            SCHEDULE_TARGET_CHAT_ID = ADMIN_CHAT_ID
        else:
            try:
                tid = int(raw_target)
            except ValueError as exc:
                raise ValueError(
                    "SCHEDULE_TARGET_CHAT_ID turi būti sveikasis skaičius (Telegram pokalbio id)."
                ) from exc
            if tid == 0:
                raise ValueError("SCHEDULE_TARGET_CHAT_ID negali būti 0.")
            SCHEDULE_TARGET_CHAT_ID = tid

    SCHEDULE_NOTIFY_ON_FAILURE = _parse_env_bool(
        os.getenv("SCHEDULE_NOTIFY_ON_FAILURE"), True
    )
