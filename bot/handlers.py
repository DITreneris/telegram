"""Komandos: admin tikrinimas, /start, /next, /status, inline navigacija."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.constants import PollType
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.bot_copy import START_MESSAGE
from orchestrator import Orchestrator
from schemas import MAX_MESSAGE_CHARS, ContentItem

logger = logging.getLogger(__name__)

_next_lock = asyncio.Lock()

_RECORD_FAILED_MSG = (
    "Delivered but could not save progress; check disk/logs — "
    "the same item may be sent again until state saves."
)


def start_nav_markup() -> InlineKeyboardMarkup:
    """One row: same actions as /next and /status (admin-only; enforced in handler)."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Next", callback_data="nav_next"),
                InlineKeyboardButton("Status", callback_data="nav_status"),
            ]
        ]
    )


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
    await update.message.reply_text(START_MESSAGE, reply_markup=start_nav_markup())


async def _run_status(
    context: ContextTypes.DEFAULT_TYPE,
    reply_text: Callable[[str], Awaitable[object]],
) -> None:
    orch: Orchestrator = context.bot_data["orchestrator"]
    try:
        text = orch.status_text()
    except (ValueError, FileNotFoundError, OSError):
        logger.exception("cmd_status: status or content error")
        await reply_text("Could not read status or content. Check logs.")
        return
    except Exception:
        logger.exception("cmd_status: unexpected error")
        await reply_text("Could not read status or content. Check logs.")
        return
    await reply_text(text)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_if_not_admin(update, context):
        return
    assert update.message
    await _run_status(context, update.message.reply_text)


async def send_content_item(bot: Bot, chat_id: int, item: ContentItem) -> None:
    """Send one manifest item to Telegram (same rules as /next delivery)."""
    if item.type == "text":
        assert item.text is not None
        for chunk in split_telegram_text_chunks(item.text):
            await bot.send_message(chat_id=chat_id, text=chunk)
        return
    if item.type == "poll":
        assert item.poll_question is not None
        assert item.poll_options is not None
        assert item.poll_correct_option_id is not None
        await bot.send_poll(
            chat_id=chat_id,
            question=item.poll_question,
            options=list(item.poll_options),
            type=PollType.QUIZ,
            correct_option_id=item.poll_correct_option_id,
        )
        if item.theme_note:
            for chunk in split_telegram_text_chunks(item.theme_note):
                await bot.send_message(chat_id=chat_id, text=chunk)
        return
    assert item.path is not None
    path = Path(item.path)
    if item.type == "photo":
        with path.open("rb") as f:
            await bot.send_photo(
                chat_id=chat_id,
                photo=InputFile(f, filename=path.name),
                caption=item.caption,
            )
        return
    if item.type == "document":
        with path.open("rb") as f:
            await bot.send_document(
                chat_id=chat_id,
                document=InputFile(f, filename=path.name),
                caption=item.caption,
            )
        return
    raise RuntimeError(f"Unknown content type (internal error): {item.type!r}")


async def _notify_admin_schedule_send_failure(
    bot: Bot,
    admin_chat_id: int,
    *,
    item: ContentItem,
    exc: BaseException,
) -> None:
    """Best-effort DM to admin when a scheduled send fails (does not re-raise)."""
    try:
        text = (
            f"Scheduled delivery failed: id={item.id}, type={item.type}. "
            f"{type(exc).__name__}: {exc}"
        )
        if len(text) > MAX_MESSAGE_CHARS:
            text = text[: MAX_MESSAGE_CHARS - 3] + "..."
        await bot.send_message(chat_id=admin_chat_id, text=text)
    except Exception:
        logger.exception("scheduled_delivery: could not notify admin")


async def run_scheduled_delivery(context: ContextTypes.DEFAULT_TYPE) -> None:
    """JobQueue callback: same sequence as /next (peek → send → record on success)."""
    raw_target = context.bot_data.get("schedule_target_chat_id")
    if raw_target is None:
        logger.error("scheduled_delivery: schedule_target_chat_id missing; skip.")
        return
    chat_id = int(raw_target)
    orch: Orchestrator = context.bot_data["orchestrator"]
    async with _next_lock:
        try:
            item = orch.peek_next_item()
        except (ValueError, FileNotFoundError, OSError):
            logger.exception("scheduled_delivery: content preparation error")
            return
        except Exception:
            logger.exception("scheduled_delivery: unexpected content preparation error")
            return
        logger.info(
            "scheduled_delivery: sending to chat_id=%s item_id=%s type=%s",
            chat_id,
            item.id,
            item.type,
        )
        try:
            await send_content_item(context.bot, chat_id, item)
        except TelegramError as exc:
            logger.exception("scheduled_delivery: telegram send error")
            if context.bot_data.get("schedule_notify_on_failure", True):
                await _notify_admin_schedule_send_failure(
                    context.bot, _admin_id(context), item=item, exc=exc
                )
            return
        except OSError as exc:
            logger.exception("scheduled_delivery: media read or io error")
            if context.bot_data.get("schedule_notify_on_failure", True):
                await _notify_admin_schedule_send_failure(
                    context.bot, _admin_id(context), item=item, exc=exc
                )
            return
        except Exception as exc:
            logger.exception("scheduled_delivery: unexpected send error")
            if context.bot_data.get("schedule_notify_on_failure", True):
                await _notify_admin_schedule_send_failure(
                    context.bot, _admin_id(context), item=item, exc=exc
                )
            return
        try:
            orch.record_delivered(item.id)
        except (OSError, ValueError):
            logger.exception(
                "scheduled_delivery: could not persist delivery state (may resend on next tick)"
            )
            if context.bot_data.get("schedule_notify_on_failure", True):
                try:
                    await context.bot.send_message(
                        chat_id=_admin_id(context),
                        text=_RECORD_FAILED_MSG,
                    )
                except Exception:
                    logger.exception(
                        "scheduled_delivery: could not notify admin after state save failure"
                    )
        except Exception:
            logger.exception(
                "scheduled_delivery: unexpected error saving delivery state (may resend on next tick)"
            )
            if context.bot_data.get("schedule_notify_on_failure", True):
                try:
                    await context.bot.send_message(
                        chat_id=_admin_id(context),
                        text=_RECORD_FAILED_MSG,
                    )
                except Exception:
                    logger.exception(
                        "scheduled_delivery: could not notify admin after state save failure"
                    )


async def _run_next(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    reply_text: Callable[[str], Awaitable[object]],
) -> None:
    orch: Orchestrator = context.bot_data["orchestrator"]
    async with _next_lock:
        try:
            item = orch.peek_next_item()
        except (ValueError, FileNotFoundError, OSError):
            logger.exception("cmd_next: content preparation error")
            await reply_text("Could not prepare content. Check logs.")
            return
        except Exception:
            logger.exception("cmd_next: unexpected content preparation error")
            await reply_text("Could not prepare content. Check logs.")
            return
        try:
            await send_content_item(context.bot, chat_id, item)
        except TelegramError:
            logger.exception("cmd_next: telegram send error")
            await reply_text("Send failed. Check logs.")
            return
        except OSError:
            logger.exception("cmd_next: media read or io error")
            await reply_text("Send failed. Check logs.")
            return
        except Exception:
            logger.exception("cmd_next: unexpected send error")
            await reply_text("Send failed. Check logs.")
            return
        try:
            orch.record_delivered(item.id)
        except (OSError, ValueError):
            logger.exception("cmd_next: could not persist delivery state")
            await reply_text(_RECORD_FAILED_MSG)
        except Exception:
            logger.exception("cmd_next: unexpected error saving delivery state")
            await reply_text(_RECORD_FAILED_MSG)


async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_if_not_admin(update, context):
        return
    assert update.message and update.effective_chat
    await _run_next(context, update.effective_chat.id, update.message.reply_text)


async def callback_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline Next / Status — same behavior as commands (admin-only)."""
    query = update.callback_query
    if query is None:
        return
    user = update.effective_user
    user_id = user.id if user else None
    if user_id != _admin_id(context):
        await query.answer("Access denied. Admin only.", show_alert=True)
        return
    await query.answer()
    if query.message is None:
        return
    chat_id = query.message.chat_id
    if query.data == "nav_next":
        await _run_next(context, chat_id, query.message.reply_text)
    elif query.data == "nav_status":
        await _run_status(context, query.message.reply_text)
