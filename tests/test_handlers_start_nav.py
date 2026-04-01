"""`/start` intro + inline Next/Status callbacks (mocked PTB)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from bot.bot_copy import START_MESSAGE
from bot.handlers import _RECORD_FAILED_MSG, callback_nav, cmd_start, start_nav_markup
from schemas import MAX_MESSAGE_CHARS, ContentItem

_ADMIN_ID = 42


def _context(orch: MagicMock) -> MagicMock:
    ctx = MagicMock()
    ctx.bot_data = {"orchestrator": orch, "admin_chat_id": _ADMIN_ID}
    ctx.bot = MagicMock()
    ctx.bot.send_message = AsyncMock()
    ctx.bot.send_photo = AsyncMock()
    ctx.bot.send_document = AsyncMock()
    ctx.bot.send_poll = AsyncMock()
    return ctx


def test_cmd_start_admin_sends_start_message_and_inline_row() -> None:
    orch = MagicMock()
    upd = MagicMock()
    upd.effective_user = MagicMock()
    upd.effective_user.id = _ADMIN_ID
    upd.message = MagicMock()
    upd.message.reply_text = AsyncMock()
    ctx = _context(orch)

    async def run() -> None:
        await cmd_start(upd, ctx)

    asyncio.run(run())

    orch.peek_next_item.assert_not_called()
    upd.message.reply_text.assert_awaited_once()
    args, kwargs = upd.message.reply_text.await_args
    assert args[0] == START_MESSAGE
    markup = kwargs.get("reply_markup")
    assert markup is not None
    row = markup.inline_keyboard[0]
    assert row[0].text == "Next" and row[0].callback_data == "nav_next"
    assert row[1].text == "Status" and row[1].callback_data == "nav_status"


def test_cmd_start_non_admin_denied() -> None:
    orch = MagicMock()
    upd = MagicMock()
    upd.effective_user = MagicMock()
    upd.effective_user.id = 999
    upd.message = MagicMock()
    upd.message.reply_text = AsyncMock()
    ctx = _context(orch)

    async def run() -> None:
        await cmd_start(upd, ctx)

    asyncio.run(run())

    upd.message.reply_text.assert_awaited_once_with("Access denied. Admin only.")
    args, kwargs = upd.message.reply_text.await_args
    assert "reply_markup" not in kwargs


def _callback_update(
    chat_id: int,
    *,
    user_id: int | None = None,
    data: str,
) -> MagicMock:
    upd = MagicMock()
    upd.effective_user = MagicMock()
    upd.effective_user.id = user_id if user_id is not None else chat_id
    upd.callback_query = MagicMock()
    upd.callback_query.data = data
    upd.callback_query.message = MagicMock()
    upd.callback_query.message.chat_id = chat_id
    upd.callback_query.message.reply_text = AsyncMock()
    upd.callback_query.answer = AsyncMock()
    return upd


def test_callback_nav_next_admin_same_as_cmd_next() -> None:
    item = ContentItem(id="n1", type="text", text="Body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    upd = _callback_update(_ADMIN_ID, data="nav_next")
    ctx = _context(orch)

    async def run() -> None:
        await callback_nav(upd, ctx)

    asyncio.run(run())

    upd.callback_query.answer.assert_awaited_once_with()
    orch.peek_next_item.assert_called_once()
    ctx.bot.send_message.assert_awaited_once_with(chat_id=_ADMIN_ID, text="Body")
    orch.record_delivered.assert_called_once_with("n1")


def test_callback_nav_next_admin_in_group() -> None:
    group_id = -1001234567890
    item = ContentItem(id="g1", type="text", text="hi")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    upd = _callback_update(group_id, user_id=_ADMIN_ID, data="nav_next")
    ctx = _context(orch)

    async def run() -> None:
        await callback_nav(upd, ctx)

    asyncio.run(run())

    ctx.bot.send_message.assert_awaited_once_with(chat_id=group_id, text="hi")
    orch.record_delivered.assert_called_once_with("g1")


def test_callback_nav_status_admin() -> None:
    orch = MagicMock()
    orch.status_text.return_value = "Queue: ok"
    upd = _callback_update(_ADMIN_ID, data="nav_status")
    ctx = _context(orch)

    async def run() -> None:
        await callback_nav(upd, ctx)

    asyncio.run(run())

    orch.status_text.assert_called_once()
    upd.callback_query.message.reply_text.assert_awaited_once_with("Queue: ok")


def test_callback_nav_non_admin_alert_no_orchestrator() -> None:
    orch = MagicMock()
    upd = _callback_update(100, user_id=999, data="nav_next")
    ctx = _context(orch)

    async def run() -> None:
        await callback_nav(upd, ctx)

    asyncio.run(run())

    orch.peek_next_item.assert_not_called()
    upd.callback_query.answer.assert_awaited_once_with(
        "Access denied. Admin only.", show_alert=True
    )


def test_start_nav_markup_matches_handler_row() -> None:
    m = start_nav_markup()
    row = m.inline_keyboard[0]
    assert len(row) == 2
    assert row[0].callback_data == "nav_next"
    assert row[1].callback_data == "nav_status"


def test_callback_nav_next_record_failure_replies() -> None:
    item = ContentItem(id="r1", type="text", text="ok")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    orch.record_delivered.side_effect = OSError("disk full")
    upd = _callback_update(_ADMIN_ID, data="nav_next")
    ctx = _context(orch)

    async def run() -> None:
        await callback_nav(upd, ctx)

    asyncio.run(run())

    upd.callback_query.message.reply_text.assert_awaited_once_with(_RECORD_FAILED_MSG)
