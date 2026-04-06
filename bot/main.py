"""PTB Application ir polling."""

from __future__ import annotations

import datetime as dt
import logging
import os
from typing import cast

import httpx
from telegram import BotCommandScopeChat, BotCommandScopeDefault
from telegram.error import Conflict, NetworkError, TimedOut
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from bot.bot_copy import bot_menu_commands
from bot.handlers import callback_nav, cmd_next, cmd_start, cmd_status, run_scheduled_delivery
from config import (
    BASE_DIR,
    BOT_TOKEN,
    CONTENT_PATH,
    resolve_log_level,
    validate_config,
)
from orchestrator import Orchestrator

logger = logging.getLogger(__name__)

# APScheduler's default misfire_grace_time is 1 second. Under polling + handlers the asyncio
# loop can start a daily job a few seconds late; APS then skips the run (EVENT_JOB_MISSED) and
# run_scheduled_delivery never runs — no bot.handlers "scheduled_delivery" log line.
_SCHEDULE_JOB_KWARGS: dict[str, int] = {"misfire_grace_time": 600}

# Local wall-clock times in SCHEDULE_TZ; one queue item per tick (same as one /next).
_SCHEDULE_DAILY_SLOTS: tuple[tuple[int, int, str], ...] = (
    (8, 0, "scheduled_morning_1"),
    (8, 15, "scheduled_morning_2"),
    (8, 30, "scheduled_morning_3"),
    (19, 0, "scheduled_evening_1"),
    (19, 15, "scheduled_evening_2"),
    (19, 30, "scheduled_evening_3"),
)

# apscheduler logs as "apscheduler.scheduler"; parent "apscheduler" alone is not enough.
_NOISY_LOGGERS = (
    "httpx",
    "httpcore",
    "apscheduler",
    "apscheduler.scheduler",
)


def _is_getupdates_conflict(err: BaseException | None, *, _depth: int = 0) -> bool:
    """True for telegram.error.Conflict even when wrapped (PTB/asyncio/TaskGroup)."""
    if err is None or _depth > 10:
        return False
    if isinstance(err, Conflict):
        return True
    if isinstance(err, BaseExceptionGroup):
        return any(
            _is_getupdates_conflict(cast(BaseException, e), _depth=_depth + 1)
            for e in err.exceptions
        )
    cause = err.__cause__
    if cause is not None and _is_getupdates_conflict(cause, _depth=_depth + 1):
        return True
    ctx = err.__context__
    if ctx is not None and ctx is not cause and _is_getupdates_conflict(
        ctx, _depth=_depth + 1
    ):
        return True
    text = str(err).lower()
    return "conflict" in text and "getupdates" in text.replace("_", "")


def _is_transient_poll_network_error(
    err: BaseException | None, *, _depth: int = 0
) -> bool:
    """True for httpx/PTB transport errors during getUpdates; PTB retries the poll loop."""
    if err is None or _depth > 10:
        return False
    if isinstance(err, (httpx.ReadError, httpx.ConnectError, httpx.TimeoutException)):
        return True
    if isinstance(err, (NetworkError, TimedOut)):
        return True
    if isinstance(err, BaseExceptionGroup):
        return any(
            _is_transient_poll_network_error(cast(BaseException, e), _depth=_depth + 1)
            for e in err.exceptions
        )
    cause = err.__cause__
    if cause is not None and _is_transient_poll_network_error(cause, _depth=_depth + 1):
        return True
    ctx = err.__context__
    if ctx is not None and ctx is not cause and _is_transient_poll_network_error(
        ctx, _depth=_depth + 1
    ):
        return True
    return False


def _quiet_third_party_loggers() -> None:
    """Host logs stay readable: polling + JobQueue spam INFO otherwise."""
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


async def error_handler(_update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if _is_getupdates_conflict(err if isinstance(err, BaseException) else None):
        logger.error(
            "Telegram Conflict: another process is already calling getUpdates for this "
            "BOT_TOKEN. Run exactly one poller: Railway single replica, no second service, "
            "stop local python run.py if hosting is active. See docs/RUNBOOK.md."
        )
        return
    base = err if isinstance(err, BaseException) else None
    if _is_transient_poll_network_error(base):
        logger.warning(
            "Transient Telegram API network error during polling (e.g. connection dropped "
            "while reading getUpdates). python-telegram-bot will retry; rare occurrences "
            "are normal. If this repeats continuously, check host connectivity to "
            "api.telegram.org and duplicate pollers (see docs/RUNBOOK.md)."
        )
        return
    logger.error("Exception while handling an update", exc_info=err)


async def post_init(application: Application) -> None:
    """Hide command menu for strangers; show start/next/status in admin private chat."""
    admin_id = int(application.bot_data["admin_chat_id"])
    await application.bot.set_my_commands([], scope=BotCommandScopeDefault())
    await application.bot.set_my_commands(
        bot_menu_commands(),
        scope=BotCommandScopeChat(chat_id=admin_id),
    )


def run_bot() -> None:
    logging.basicConfig(
        level=resolve_log_level(),
        format="%(levelname)s %(name)s %(message)s",
    )
    _quiet_third_party_loggers()
    validate_config()
    # Values are set inside validate_config(); avoid stale import-time defaults.
    from config import (
        ADMIN_CHAT_ID,
        ENABLE_SCHEDULED_POSTING,
        ENABLE_X_POSTING,
        SCHEDULE_NOTIFY_ON_FAILURE,
        SCHEDULE_TARGET_CHAT_ID,
        SCHEDULE_TIMEZONE,
        STATE_PATH,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        X_NOTIFY_ON_FAILURE,
    )

    assert ADMIN_CHAT_ID is not None
    orch = Orchestrator(
        content_path=CONTENT_PATH,
        state_path=STATE_PATH,
        base_dir=BASE_DIR,
    )
    orch.load_manifest()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.bot_data["orchestrator"] = orch
    # Numeric Telegram user id for the admin (env name ADMIN_CHAT_ID unchanged).
    application.bot_data["admin_chat_id"] = ADMIN_CHAT_ID
    application.bot_data["schedule_target_chat_id"] = (
        SCHEDULE_TARGET_CHAT_ID if ENABLE_SCHEDULED_POSTING else None
    )
    application.bot_data["schedule_notify_on_failure"] = SCHEDULE_NOTIFY_ON_FAILURE
    application.bot_data["enable_x_posting"] = ENABLE_X_POSTING
    application.bot_data["x_notify_on_failure"] = X_NOTIFY_ON_FAILURE
    application.bot_data["x_twitter_credentials"] = (
        {
            "api_key": TWITTER_API_KEY,
            "api_secret": TWITTER_API_SECRET,
            "access_token": TWITTER_ACCESS_TOKEN,
            "access_token_secret": TWITTER_ACCESS_TOKEN_SECRET,
        }
        if ENABLE_X_POSTING
        else None
    )

    if ENABLE_SCHEDULED_POSTING:
        assert SCHEDULE_TIMEZONE is not None and SCHEDULE_TARGET_CHAT_ID is not None
        jq = application.job_queue
        if jq is None:
            raise RuntimeError(
                "ENABLE_SCHEDULED_POSTING is set but JobQueue is unavailable. "
                "Install dependencies with: pip install -r requirements.txt"
            )
        # run_daily touches APScheduler before run_polling; re-apply levels here too.
        _quiet_third_party_loggers()
        for hour, minute, job_name in _SCHEDULE_DAILY_SLOTS:
            jq.run_daily(
                run_scheduled_delivery,
                time=dt.time(hour, minute, tzinfo=SCHEDULE_TIMEZONE),
                name=job_name,
                job_kwargs=_SCHEDULE_JOB_KWARGS,
            )
        logger.info(
            "Scheduled posting enabled: 08:00, 08:15, 08:30, 19:00, 19:15, 19:30 %s → chat_id=%s",
            SCHEDULE_TIMEZONE.key,
            SCHEDULE_TARGET_CHAT_ID,
        )

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("next", cmd_next))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(
        CallbackQueryHandler(callback_nav, pattern=r"^nav_(next|status)$")
    )
    application.add_error_handler(error_handler)

    _rail_sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "").strip()
    logger.info(
        "Queue bot polling started (scheduled_posting=%s, x_posting=%s, railway_git_sha=%s)",
        ENABLE_SCHEDULED_POSTING,
        ENABLE_X_POSTING,
        _rail_sha or "n/a",
    )
    # Libraries may attach loggers after import; re-apply before the poll loop.
    _quiet_third_party_loggers()
    application.run_polling(drop_pending_updates=True)
