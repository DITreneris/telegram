"""Scheduled JobQueue callback: peek → send → record (mocked)."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call, patch

from telegram.constants import PollType
from telegram.error import TelegramError

from bot.handlers import _RECORD_FAILED_MSG, run_scheduled_delivery
from schemas import ContentItem

_TARGET_CHAT = 999888777
_ADMIN_CHAT_ID = 111222333

_X_CREDENTIALS = {
    "api_key": "k",
    "api_secret": "ks",
    "access_token": "t",
    "access_token_secret": "ts",
}


def _context(orch: MagicMock, *, notify_on_failure: bool = True) -> MagicMock:
    ctx = MagicMock()
    ctx.bot_data = {
        "orchestrator": orch,
        "schedule_target_chat_id": _TARGET_CHAT,
        "admin_chat_id": _ADMIN_CHAT_ID,
        "schedule_notify_on_failure": notify_on_failure,
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


def test_run_scheduled_delivery_telegram_error_notifies_admin() -> None:
    item = ContentItem(id="s3", type="text", text="body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    context = _context(orch)
    context.bot.send_message = AsyncMock(
        side_effect=[TelegramError("blocked"), None],
    )

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    orch.record_delivered.assert_not_called()
    assert context.bot.send_message.await_count == 2
    calls = context.bot.send_message.await_args_list
    assert calls[0].kwargs["chat_id"] == _TARGET_CHAT
    assert calls[1].kwargs["chat_id"] == _ADMIN_CHAT_ID
    assert "Scheduled delivery failed" in calls[1].kwargs["text"]
    assert "s3" in calls[1].kwargs["text"]
    assert "text" in calls[1].kwargs["text"]


def test_run_scheduled_delivery_telegram_error_skips_notify_when_disabled() -> None:
    item = ContentItem(id="s4", type="text", text="body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    context = _context(orch, notify_on_failure=False)
    context.bot.send_message = AsyncMock(side_effect=TelegramError("blocked"))

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    orch.record_delivered.assert_not_called()
    context.bot.send_message.assert_awaited_once_with(
        chat_id=_TARGET_CHAT, text="body"
    )


def test_run_scheduled_delivery_record_failure_notifies_admin() -> None:
    item = ContentItem(id="s5", type="text", text="body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    orch.record_delivered.side_effect = OSError("disk full")
    context = _context(orch)

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    assert context.bot.send_message.await_count == 2
    calls = context.bot.send_message.await_args_list
    assert calls[0].kwargs["chat_id"] == _TARGET_CHAT
    assert calls[0].kwargs["text"] == "body"
    assert calls[1].kwargs["chat_id"] == _ADMIN_CHAT_ID
    assert calls[1].kwargs["text"] == _RECORD_FAILED_MSG


def test_run_scheduled_delivery_record_failure_skips_notify_when_disabled() -> None:
    item = ContentItem(id="s6", type="text", text="body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    orch.record_delivered.side_effect = OSError("disk full")
    context = _context(orch, notify_on_failure=False)

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    context.bot.send_message.assert_awaited_once_with(
        chat_id=_TARGET_CHAT, text="body"
    )


def test_run_scheduled_delivery_missing_target_skips() -> None:
    orch = MagicMock()
    ctx = MagicMock()
    ctx.bot_data = {"orchestrator": orch}
    ctx.bot = MagicMock()

    async def run() -> None:
        await run_scheduled_delivery(ctx)

    asyncio.run(run())

    orch.peek_next_item.assert_not_called()


@patch("bot.handlers.post_photo_with_caption")
def test_run_scheduled_delivery_photo_with_x_posting(mock_x_post, tmp_path: Path) -> None:
    img = tmp_path / "s.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n\x00")
    item = ContentItem(id="sph", type="photo", path=str(img), caption="h")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    orch.is_x_posted.return_value = False
    context = _context(orch)
    context.bot_data["enable_x_posting"] = True
    context.bot_data["x_twitter_credentials"] = _X_CREDENTIALS

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    mock_x_post.assert_called_once()
    orch.mark_x_posted.assert_called_once_with("sph")
    orch.record_delivered.assert_called_once_with("sph")


@patch("bot.handlers.post_photo_with_caption")
def test_run_scheduled_delivery_photo_x_failure_still_records(
    mock_x_post, tmp_path: Path
) -> None:
    mock_x_post.side_effect = OSError("x api")
    img = tmp_path / "s2.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n\x00")
    item = ContentItem(id="sph2", type="photo", path=str(img), caption="h")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    orch.is_x_posted.return_value = False
    context = _context(orch)
    context.bot_data["enable_x_posting"] = True
    context.bot_data["x_twitter_credentials"] = _X_CREDENTIALS

    async def run() -> None:
        await run_scheduled_delivery(context)

    asyncio.run(run())

    orch.mark_x_posted.assert_not_called()
    orch.record_delivered.assert_called_once_with("sph2")
    calls = context.bot.send_message.await_args_list
    assert any(
        c.kwargs.get("chat_id") == _ADMIN_CHAT_ID
        and "X (Twitter) post failed" in c.kwargs.get("text", "")
        for c in calls
    )
