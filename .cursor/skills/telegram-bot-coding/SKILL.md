---
name: telegram-bot-coding
description: >-
  Edits and extends the 63_telegram_bot Python codebase using python-telegram-bot
  (Application, CommandHandler, async handlers), Orchestrator, schemas, and config.
  Use when implementing or fixing bot commands, content delivery, manifest handling,
  state, or deployment-related Python in this repository.
---

# Telegram bot coding (63_telegram_bot)

## Before changing code

1. Read [AGENTS.md](../../../AGENTS.md) for the module map and run command.
2. For behavior and data flow, skim [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md).
3. For env and runtime issues, use [docs/RUNBOOK.md](../../../docs/RUNBOOK.md).

## Conventions

- **Handlers** live in `bot/handlers.py`; register new commands in `bot/main.py`.
- Use `context.bot_data["orchestrator"]` and `context.bot_data["admin_chat_id"]`. Keep the admin gate for privileged actions.
- **Orchestration** (next item, state, status text) stays in `orchestrator.py`; **validation** in `schemas.py` / `content_loader.py`.
- **User-visible strings** (Telegram messages) stay **English** unless the user explicitly requests another language.
- Prefer small, focused diffs; match existing typing and `from __future__ import annotations`.

## Checklist for a new command

- [ ] Async handler in `bot/handlers.py` with admin check if restricted
- [ ] `CommandHandler` added in `bot/main.py`
- [ ] No duplicated manifest rules — extend `schemas.py` if the manifest shape changes
- [ ] Run `pytest` from repo root after substantive Python edits (`requirements-dev.txt`)
- [ ] If behavior is user-facing or operational, update `docs/` and [docs/INDEX.md](../../../docs/INDEX.md); for notable changes add [CHANGELOG.md](../../../CHANGELOG.md) per [VERSIONING.md](../../../docs/VERSIONING.md) (`[Unreleased]` or the version section you ship)

## Quick reference

| Task | Primary files |
|------|----------------|
| New / changed command | `bot/handlers.py`, `bot/main.py` |
| Queue or state logic | `orchestrator.py`, `state_store.py` |
| content.json shape | `schemas.py`, `content_loader.py`, sample `data/content.json` |
| Secrets / paths | `config.py`, `.env.example`, [RUNBOOK.md](../../../docs/RUNBOOK.md) |
