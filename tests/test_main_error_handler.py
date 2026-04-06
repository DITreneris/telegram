"""bot.main error_handler edge cases."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import MagicMock

import httpx
import pytest
from telegram.error import Conflict, NetworkError, TelegramError, TimedOut

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


def test_error_handler_conflict_wrapped_in_exception_group(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = ExceptionGroup(
        "nested",
        (Conflict("terminated by other getUpdates request"),),
    )

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    messages = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(messages) == 1
    assert "Telegram Conflict" in messages[0]


def test_error_handler_conflict_as_cause(
    caplog: pytest.LogCaptureFixture,
) -> None:
    try:
        raise Conflict("terminated by other getUpdates request")
    except Conflict as exc:
        wrapped = RuntimeError("wrapper")
        wrapped.__cause__ = exc
        ctx = MagicMock()
        ctx.error = wrapped

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    messages = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(messages) == 1
    assert "Telegram Conflict" in messages[0]


def test_error_handler_conflict_detected_by_message(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = TelegramError(
        "Conflict: terminated by other getUpdates request; make sure that only one bot "
        "instance is running"
    )

    with caplog.at_level(logging.ERROR, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    messages = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(messages) == 1
    assert "Telegram Conflict" in messages[0]


def test_error_handler_httpx_read_error_logs_warning_not_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = httpx.ReadError("connection dropped")

    with caplog.at_level(logging.WARNING, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    assert not any(
        "Exception while handling an update" in r.getMessage()
        for r in caplog.records
        if r.levelno >= logging.ERROR
    )
    assert any(
        "Transient Telegram API network error" in r.getMessage()
        for r in caplog.records
        if r.levelno == logging.WARNING
    )


def test_error_handler_network_error_logs_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = NetworkError("Bad Gateway")

    with caplog.at_level(logging.WARNING, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    assert not any(r.levelno >= logging.ERROR for r in caplog.records)
    assert any(
        "Transient Telegram API network error" in r.getMessage()
        for r in caplog.records
        if r.levelno == logging.WARNING
    )


def test_error_handler_timed_out_logs_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ctx = MagicMock()
    ctx.error = TimedOut()

    with caplog.at_level(logging.WARNING, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    assert not any(r.levelno >= logging.ERROR for r in caplog.records)
    assert any(
        "Transient Telegram API network error" in r.getMessage()
        for r in caplog.records
        if r.levelno == logging.WARNING
    )


def test_error_handler_read_error_as_cause_logs_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    try:
        raise httpx.ReadError("eof")
    except httpx.ReadError as exc:
        wrapped = RuntimeError("wrapper")
        wrapped.__cause__ = exc
        ctx = MagicMock()
        ctx.error = wrapped

    with caplog.at_level(logging.WARNING, logger="bot.main"):
        asyncio.run(error_handler(None, ctx))

    assert not any(r.levelno >= logging.ERROR for r in caplog.records)
    assert any(
        "Transient Telegram API network error" in r.getMessage()
        for r in caplog.records
        if r.levelno == logging.WARNING
    )
