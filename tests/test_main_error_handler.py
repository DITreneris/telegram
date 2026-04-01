"""bot.main error_handler edge cases."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import MagicMock

import pytest
from telegram.error import Conflict, TelegramError

from bot.main import error_handler


def test_error_handler_conflict_logs_single_operator_hint(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = Conflict("terminated by other getUpdates request")

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    messages = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(messages) == 1
    assert "Telegram Conflict" in messages[0]
    assert "getUpdates" in messages[0]


def test_error_handler_other_error_uses_exc_info(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = TelegramError("other")

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    assert any(
        "Exception while handling an update" in r.getMessage()
        for r in caplog.records
        if r.levelno >= logging.ERROR
    )
