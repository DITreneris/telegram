"""Komandos: admin tikrinimas, /start, /next, /status."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from telegram import InputFile, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from orchestrator import Orchestrator
from schemas import ContentItem

logger = logging.getLogger(__name__)

_next_lock = asyncio.Lock()

_RECORD_FAILED_MSG = (
    "Delivered but could not save progress; check disk/logs — may resend on next /next."
)

# Same limit as Telegram Bot API sendMessage and api/publish.ts.
MAX_MESSAGE_CHARS = 4096


def split_telegram_text_chunks(text: str) -> list[str]:
    """Split body text so each part fits Telegram's message length limit."""
    if len(text) <= MAX_MESSAGE_CHARS:
        return [text]
    return [text[i : i + MAX_MESSAGE_CHARS] for i in range(0, len(text), MAX_MESSAGE_CHARS)]


def _admin_id(context: ContextTypes.DEFAULT_TYPE) -> int:
    return int(context.bot_data["admin_chat_id"])


async def _deny_if_not_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    user_id = user.id if user else None
    if user_id != _admin_id(context):
        if update.message:
            await update.message.reply_text("Access denied. Admin only.")
        return True
    return False


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_if_not_admin(update, context):
        return
    assert update.message
    await update.message.reply_text(
        "Lean orchestrator (MVP).\n"
        "Commands:\n"
        "/next — next queued item (cycles)\n"
        "/status — status"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_if_not_admin(update, context):
        return
    assert update.message
    orch: Orchestrator = context.bot_data["orchestrator"]
    try:
        text = orch.status_text()
    except (ValueError, FileNotFoundError, OSError):
        logger.exception("cmd_status: status or content error")
        await update.message.reply_text("Could not read status or content. Check logs.")
        return
    except Exception:
        logger.exception("cmd_status: unexpected error")
        await update.message.reply_text("Could not read status or content. Check logs.")
        return
    await update.message.reply_text(text)


async def _send_item(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    item: ContentItem,
) -> None:
    assert update.effective_chat
    chat_id = update.effective_chat.id
    if item.type == "text":
        assert item.text is not None
        for chunk in split_telegram_text_chunks(item.text):
            await context.bot.send_message(chat_id=chat_id, text=chunk)
        return
    assert item.path is not None
    path = Path(item.path)
    if item.type == "photo":
        with path.open("rb") as f:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=InputFile(f, filename=path.name),
                caption=item.caption,
            )
        return
    if item.type == "document":
        with path.open("rb") as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=InputFile(f, filename=path.name),
                caption=item.caption,
            )
        return
    raise RuntimeError(f"Unknown content type (internal error): {item.type!r}")


async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_if_not_admin(update, context):
        return
    assert update.message
    orch: Orchestrator = context.bot_data["orchestrator"]
    async with _next_lock:
        try:
            item = orch.peek_next_item()
        except (ValueError, FileNotFoundError, OSError):
            logger.exception("cmd_next: content preparation error")
            await update.message.reply_text("Could not prepare content. Check logs.")
            return
        except Exception:
            logger.exception("cmd_next: unexpected content preparation error")
            await update.message.reply_text("Could not prepare content. Check logs.")
            return
        try:
            await _send_item(update, context, item)
        except TelegramError:
            logger.exception("cmd_next: telegram send error")
            await update.message.reply_text("Send failed. Check logs.")
            return
        except OSError:
            logger.exception("cmd_next: media read or io error")
            await update.message.reply_text("Send failed. Check logs.")
            return
        except Exception:
            logger.exception("cmd_next: unexpected send error")
            await update.message.reply_text("Send failed. Check logs.")
            return
        try:
            orch.record_delivered(item.id)
        except (OSError, ValueError):
            logger.exception("cmd_next: could not persist delivery state")
            await update.message.reply_text(_RECORD_FAILED_MSG)
        except Exception:
            logger.exception("cmd_next: unexpected error saving delivery state")
            await update.message.reply_text(_RECORD_FAILED_MSG)
