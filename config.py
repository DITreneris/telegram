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
# Default; validate_config() may set a different path from QUEUE_STATE_PATH (e.g. Railway volume).
STATE_PATH: Path = BASE_DIR / "data" / "state.json"

_LOG_LEVEL_NAMES = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID: int | None = None

ENABLE_SCHEDULED_POSTING = False
SCHEDULE_TIMEZONE: ZoneInfo | None = None
SCHEDULE_TARGET_CHAT_ID: int | None = None
SCHEDULE_NOTIFY_ON_FAILURE = True

ENABLE_X_POSTING = False
X_NOTIFY_ON_FAILURE = True
TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""


def resolve_log_level() -> int:
    """Return logging level from LOG_LEVEL (default INFO). Unknown values fall back to INFO."""
    raw = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if not raw or raw not in _LOG_LEVEL_NAMES:
        if raw and raw not in _LOG_LEVEL_NAMES:
            warnings.warn(
                f'LOG_LEVEL {os.getenv("LOG_LEVEL", "")!r} is not recognized; using INFO.',
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
    global ENABLE_X_POSTING, X_NOTIFY_ON_FAILURE
    global TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
    global STATE_PATH
    if not BOT_TOKEN:
        raise ValueError(
            "Set the BOT_TOKEN environment variable or add it to your .env file."
        )
    raw = os.getenv("ADMIN_CHAT_ID", "").strip()
    if not raw:
        raise ValueError(
            "Set the ADMIN_CHAT_ID environment variable or add it to your .env file "
            "(integer, non-zero)."
        )
    try:
        aid = int(raw)
    except ValueError as exc:
        raise ValueError(
            "ADMIN_CHAT_ID must be an integer (e.g. your Telegram user or chat id)."
        ) from exc
    if aid == 0:
        raise ValueError("ADMIN_CHAT_ID cannot be 0.")
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
                f"Unknown SCHEDULE_TZ: {tz_name!r} (use an IANA timezone, e.g. \"Europe/Vilnius\")."
            ) from exc

        raw_target = (os.getenv("SCHEDULE_TARGET_CHAT_ID") or "").strip()
        if not raw_target:
            SCHEDULE_TARGET_CHAT_ID = ADMIN_CHAT_ID
        else:
            try:
                tid = int(raw_target)
            except ValueError as exc:
                raise ValueError(
                    "SCHEDULE_TARGET_CHAT_ID must be an integer (Telegram chat id)."
                ) from exc
            if tid == 0:
                raise ValueError("SCHEDULE_TARGET_CHAT_ID cannot be 0.")
            SCHEDULE_TARGET_CHAT_ID = tid

    SCHEDULE_NOTIFY_ON_FAILURE = _parse_env_bool(
        os.getenv("SCHEDULE_NOTIFY_ON_FAILURE"), True
    )

    ENABLE_X_POSTING = _parse_env_bool(os.getenv("ENABLE_X_POSTING"), False)
    X_NOTIFY_ON_FAILURE = _parse_env_bool(os.getenv("X_NOTIFY_ON_FAILURE"), True)
    TWITTER_API_KEY = ""
    TWITTER_API_SECRET = ""
    TWITTER_ACCESS_TOKEN = ""
    TWITTER_ACCESS_TOKEN_SECRET = ""

    if ENABLE_X_POSTING:
        t_key = os.getenv("TWITTER_API_KEY", "").strip()
        t_secret = os.getenv("TWITTER_API_SECRET", "").strip()
        t_token = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
        t_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "").strip()
        missing = [
            name
            for name, val in (
                ("TWITTER_API_KEY", t_key),
                ("TWITTER_API_SECRET", t_secret),
                ("TWITTER_ACCESS_TOKEN", t_token),
                ("TWITTER_ACCESS_TOKEN_SECRET", t_token_secret),
            )
            if not val
        ]
        if missing:
            raise ValueError(
                "ENABLE_X_POSTING is set but the following env vars are missing or empty: "
                + ", ".join(missing)
            )
        TWITTER_API_KEY = t_key
        TWITTER_API_SECRET = t_secret
        TWITTER_ACCESS_TOKEN = t_token
        TWITTER_ACCESS_TOKEN_SECRET = t_token_secret

    raw_state = (os.getenv("QUEUE_STATE_PATH") or "").strip()
    if raw_state:
        candidate = Path(raw_state)
        STATE_PATH = (
            candidate.resolve()
            if candidate.is_absolute()
            else (BASE_DIR / candidate).resolve()
        )
    else:
        STATE_PATH = (BASE_DIR / "data" / "state.json").resolve()
