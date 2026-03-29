"""PTB Application ir polling."""

from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler, ContextTypes

from bot.handlers import cmd_next, cmd_start, cmd_status
from config import (
    ADMIN_CHAT_ID,
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


def run_bot() -> None:
    logging.basicConfig(
        level=resolve_log_level(),
        format="%(levelname)s %(name)s %(message)s",
    )
    validate_config()
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
        .build()
    )
    application.bot_data["orchestrator"] = orch
    # Numeric Telegram user id for the admin (env name ADMIN_CHAT_ID unchanged).
    application.bot_data["admin_chat_id"] = ADMIN_CHAT_ID

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("next", cmd_next))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_error_handler(error_handler)

    application.run_polling(drop_pending_updates=True)
