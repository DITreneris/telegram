"""Canonical English copy for /start, BotFather, and Telegram command menu.

For BotFather: copy only the **plain string value** (what you see between the quotes),
not parentheses or multiple quoted fragments — that is Python source, not BotFather input.
"""

from __future__ import annotations

from telegram import BotCommand

# BotFather /setdescription — short blurb (Telegram limit 512 chars; keep brief).
BOTFATHER_SHORT_DESCRIPTION = (
    "Admin-only curriculum queue: send the next item (text, photo, document, or quiz poll) "
    "to this chat."
)

# BotFather /setabouttext — profile “About” (≤ 120 chars). Copy only the characters inside the quotes.
BOTFATHER_ABOUT = "Private admin bot for managing a Telegram content queue. Use /next to post the next item and /status to check progress."

# /start reply body (must stay English for user-facing bot text).
START_MESSAGE = (
    "Lean queue orchestrator (MVP).\n\n"
    "• /next — send the next queued item (text, photo, document, or quiz poll; cycles)\n"
    "• /status — queue summary and next item (id and type)\n\n"
    "Or use the buttons below."
)


def bot_menu_commands() -> list[BotCommand]:
    """Descriptions for set_my_commands (admin private chat scope)."""
    return [
        BotCommand("start", "Intro and shortcut buttons"),
        BotCommand("next", "Send next queued item to this chat"),
        BotCommand("status", "Queue summary and next item"),
    ]
