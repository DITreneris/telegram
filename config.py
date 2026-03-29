"""Load env and paths. Validated at bot startup."""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CONTENT_PATH = BASE_DIR / "data" / "content.json"
STATE_PATH = BASE_DIR / "data" / "state.json"

_LOG_LEVEL_NAMES = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID: int | None = None


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


def validate_config() -> None:
    global ADMIN_CHAT_ID
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
