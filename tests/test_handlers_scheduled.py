"""Scheduled JobQueue callback: peek → send → record (mocked)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, call

from telegram.constants import PollType

from bot.handlers import run_scheduled_delivery
from schemas import ContentItem

_TARGET_CHAT = 999888777


def _context(orch: MagicMock) -> MagicMock:
    ctx = MagicMock()
    ctx.bot_data = {
        "orchestrator": orch,
        "schedule_target_chat_id": _TARGET_CHAT,
    }
    ctx.bot = MagicMock()
    ctx.bot.send_message = AsyncMock()
    ctx.bot.send_photo = AsyncMock()
    ctx.bot.send_document = AsyncMock()
    ctx.bot.send_poll = AsyncMock()
    return ctx


def test_run_scheduled_delivery_poll_sends_quiz() -> None:
    item = ContentItem(
        id="sp1",
        type="poll",
        poll_question="Quiz?",
        poll_options=("A", "B"),
        poll_correct_option_id=0,
    )
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    context = _context(orch)

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    context.bot.send_poll.assert_awaited_once_with(
        chat_id=_TARGET_CHAT,
        question="Quiz?",
        options=["A", "B"],
        type=PollType.QUIZ,
        correct_option_id=0,
    )
    orch.record_delivered.assert_called_once_with("sp1")


def test_run_scheduled_delivery_poll_with_theme_note_sends_debrief() -> None:
    item = ContentItem(
        id="sp2",
        type="poll",
        poll_question="Quiz?",
        poll_options=("A", "B"),
        poll_correct_option_id=0,
        theme_note="Takeaway after quiz.",
    )
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    context = _context(orch)

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    context.bot.send_poll.assert_awaited_once_with(
        chat_id=_TARGET_CHAT,
        question="Quiz?",
        options=["A", "B"],
        type=PollType.QUIZ,
        correct_option_id=0,
    )
    context.bot.send_message.assert_awaited_once_with(
        chat_id=_TARGET_CHAT, text="Takeaway after quiz."
    )
    orch.record_delivered.assert_called_once_with("sp2")


def test_run_scheduled_delivery_peek_send_record() -> None:
    item = ContentItem(id="s1", type="text", text="Scheduled body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    context = _context(orch)

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    context.bot.send_message.assert_awaited_once_with(
        chat_id=_TARGET_CHAT, text="Scheduled body"
    )
    orch.record_delivered.assert_called_once_with("s1")
    assert orch.mock_calls == [call.peek_next_item(), call.record_delivered("s1")]


def test_run_scheduled_delivery_send_error_does_not_record() -> None:
    item = ContentItem(id="s2", type="text", text="x")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    context = _context(orch)
    context.bot.send_message.side_effect = OSError("disk")

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    orch.record_delivered.assert_not_called()


def test_run_scheduled_delivery_missing_target_skips() -> None:
    orch = MagicMock()
    ctx = MagicMock()
    ctx.bot_data = {"orchestrator": orch}
    ctx.bot = MagicMock()

    async def run() -> None:
        await run_scheduled_delivery(ctx)

    asyncio.run(run())

    orch.peek_next_item.assert_not_called()
