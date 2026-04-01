"""PTB Application ir polling."""

from __future__ import annotations

import datetime as dt
import logging

from telegram import BotCommandScopeChat, BotCommandScopeDefault
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from bot.bot_copy import bot_menu_commands
from bot.handlers import callback_nav, cmd_next, cmd_start, cmd_status, run_scheduled_delivery
from config import (
    BASE_DIR,
    BOT_TOKEN,
    CONTENT_PATH,
    STATE_PATH,
    resolve_log_level,
    validate_config,
)
from orchestrator import Orchestrator

logger = logging.getLogger(__name__)


async def error_handler(_update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update", exc_info=context.error)


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
    # Long polling issues a successful getUpdates HTTP call every few seconds; at INFO
    # that drowns out bot.main / scheduled_delivery lines in host log UIs.
    for _noisy in ("httpx", "httpcore"):
        logging.getLogger(_noisy).setLevel(logging.WARNING)
    validate_config()
    # Values are set inside validate_config(); avoid stale import-time defaults.
    from config import (
        ADMIN_CHAT_ID,
        ENABLE_SCHEDULED_POSTING,
        SCHEDULE_NOTIFY_ON_FAILURE,
        SCHEDULE_TARGET_CHAT_ID,
        SCHEDULE_TIMEZONE,
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

    if ENABLE_SCHEDULED_POSTING:
        assert SCHEDULE_TIMEZONE is not None and SCHEDULE_TARGET_CHAT_ID is not None
        jq = application.job_queue
        if jq is None:
            raise RuntimeError(
                "ENABLE_SCHEDULED_POSTING is set but JobQueue is unavailable. "
                "Install dependencies with: pip install -r requirements.txt"
            )
        t_morning_1 = dt.time(8, 0, tzinfo=SCHEDULE_TIMEZONE)
        t_morning_2 = dt.time(8, 30, tzinfo=SCHEDULE_TIMEZONE)
        t_evening_1 = dt.time(19, 0, tzinfo=SCHEDULE_TIMEZONE)
        t_evening_2 = dt.time(19, 30, tzinfo=SCHEDULE_TIMEZONE)
        jq.run_daily(
            run_scheduled_delivery, time=t_morning_1, name="scheduled_morning_1"
        )
        jq.run_daily(
            run_scheduled_delivery, time=t_morning_2, name="scheduled_morning_2"
        )
        jq.run_daily(
            run_scheduled_delivery, time=t_evening_1, name="scheduled_evening_1"
        )
        jq.run_daily(
            run_scheduled_delivery, time=t_evening_2, name="scheduled_evening_2"
        )
        logger.info(
            "Scheduled posting enabled: 08:00, 08:30, 19:00, 19:30 %s → chat_id=%s",
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

    logger.info(
        "Queue bot polling started (scheduled_posting=%s)",
        ENABLE_SCHEDULED_POSTING,
    )
    application.run_polling(drop_pending_updates=True)
