"""Canonical English copy for /start, BotFather, and Telegram command menu.

Paste BotFather fields manually from these constants when they change.
"""

from __future__ import annotations

from telegram import BotCommand

# BotFather /setdescription — short blurb (Telegram limit 512 chars; keep brief).
BOTFATHER_SHORT_DESCRIPTION = (
    "Admin-only curriculum queue: send the next item (text, photo, document, or quiz poll) "
    "to this chat."
)

# BotFather /setabouttext — profile “About”.
BOTFATHER_ABOUT = (
    "Private admin tool for this project’s Telegram curriculum queue. "
    "Only the configured admin can run commands. "
    "Use /next to deliver the next manifest item to the current chat, "
    "/status for queue summary, /start for the intro and shortcut buttons. "
    "Content order comes from data/content.json (regenerated from posts + polls)."
)

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
