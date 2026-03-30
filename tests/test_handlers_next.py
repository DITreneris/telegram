"""`/next` handler contract: peek → send → record only after success (mocked PTB)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, call

from bot.handlers import MAX_MESSAGE_CHARS, _RECORD_FAILED_MSG, cmd_next
from schemas import ContentItem

_ADMIN_ID = 42


def _context(orch: MagicMock) -> MagicMock:
    ctx = MagicMock()
    ctx.bot_data = {"orchestrator": orch, "admin_chat_id": _ADMIN_ID}
    ctx.bot = MagicMock()
    ctx.bot.send_message = AsyncMock()
    ctx.bot.send_photo = AsyncMock()
    ctx.bot.send_document = AsyncMock()
    return ctx


def _update(chat_id: int, *, user_id: int | None = None) -> MagicMock:
    upd = MagicMock()
    upd.effective_chat = MagicMock()
    upd.effective_chat.id = chat_id
    upd.effective_user = MagicMock()
    upd.effective_user.id = user_id if user_id is not None else chat_id
    upd.message = MagicMock()
    upd.message.reply_text = AsyncMock()
    return upd


def test_cmd_next_peek_then_send_then_record() -> None:
    item = ContentItem(id="n1", type="text", text="Body")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    update = _update(_ADMIN_ID)
    context = _context(orch)

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    context.bot.send_message.assert_awaited_once_with(chat_id=_ADMIN_ID, text="Body")
    orch.record_delivered.assert_called_once_with("n1")
    assert orch.mock_calls == [call.peek_next_item(), call.record_delivered("n1")]


def test_cmd_next_long_text_sends_multiple_messages_then_records_once() -> None:
    chunk_a = "a" * MAX_MESSAGE_CHARS
    chunk_b = "bb"
    body = chunk_a + chunk_b
    item = ContentItem(id="long1", type="text", text=body)
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    update = _update(_ADMIN_ID)
    context = _context(orch)

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    assert context.bot.send_message.await_args_list == [
        call(chat_id=_ADMIN_ID, text=chunk_a),
        call(chat_id=_ADMIN_ID, text=chunk_b),
    ]
    orch.record_delivered.assert_called_once_with("long1")


def test_cmd_next_peek_error_does_not_record() -> None:
    orch = MagicMock()
    orch.peek_next_item.side_effect = ValueError("bad manifest")
    update = _update(_ADMIN_ID)
    context = _context(orch)

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    orch.record_delivered.assert_not_called()
    context.bot.send_message.assert_not_called()
    update.message.reply_text.assert_awaited()


def test_cmd_next_send_error_does_not_record() -> None:
    orch = MagicMock()
    orch.peek_next_item.return_value = ContentItem(id="x", type="text", text="t")
    update = _update(_ADMIN_ID)
    context = _context(orch)
    context.bot.send_message.side_effect = RuntimeError("send failed")

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    context.bot.send_message.assert_awaited_once()
    orch.record_delivered.assert_not_called()
    update.message.reply_text.assert_awaited()


def test_cmd_next_non_admin_skips_orchestrator() -> None:
    orch = MagicMock()
    update = _update(100, user_id=999)
    context = _context(orch)

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    orch.peek_next_item.assert_not_called()
    orch.record_delivered.assert_not_called()
    update.message.reply_text.assert_awaited_once_with("Access denied. Admin only.")


def test_cmd_next_record_failure_after_send() -> None:
    item = ContentItem(id="r1", type="text", text="ok")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    orch.record_delivered.side_effect = OSError("disk full")
    update = _update(_ADMIN_ID)
    context = _context(orch)

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    orch.peek_next_item.assert_called_once()
    context.bot.send_message.assert_awaited_once_with(chat_id=_ADMIN_ID, text="ok")
    orch.record_delivered.assert_called_once_with("r1")
    update.message.reply_text.assert_awaited_once_with(_RECORD_FAILED_MSG)


def test_cmd_next_admin_in_group() -> None:
    group_id = -1001234567890
    item = ContentItem(id="g1", type="text", text="hi")
    orch = MagicMock()
    orch.peek_next_item.return_value = item
    update = _update(group_id, user_id=_ADMIN_ID)
    context = _context(orch)

    async def run() -> None:
        await cmd_next(update, context)

    asyncio.run(run())

    context.bot.send_message.assert_awaited_once_with(chat_id=group_id, text="hi")
    orch.record_delivered.assert_called_once_with("g1")
