# Runbook

## Prerequisites

- Python 3.10+ recommended (project uses modern typing: `float | None`, `from __future__ import annotations`).
- A Telegram bot token from [@BotFather](https://t.me/BotFather).
- Your Telegram user id for `ADMIN_CHAT_ID` (e.g. from [@userinfobot](https://t.me/userinfobot) or similar).

## Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate it (Windows): `.venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set variables (see below).
5. From the **repository root**: `python run.py`

## Running tests

1. Install dev dependencies: `pip install -r requirements-dev.txt` (includes `pytest` and app requirements).
2. From the **repository root**: `pytest`

Tests live under `tests/`; `pytest.ini` sets `pythonpath` so imports resolve from the repo root.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from BotFather |
| `ADMIN_CHAT_ID` | Yes | Your Telegram **user** id (same as [`.env.example`](../.env.example)); the bot compares it to `update.effective_user.id` for **authorization**. Messages are still sent to `update.effective_chat.id` (private chat or group where you run the command). |
| `LOG_LEVEL` | No | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` (default `INFO`; unknown values fall back to `INFO` with a warning) |

If either required variable is missing or invalid at startup, `validate_config()` in `config.py` raises a clear error.

Commented keys under „Ateičiai“ in [`.env.example`](../.env.example) are placeholders for future features; they are not read by the bot until implemented.

## Content manifest

- Default path: `data/content.json` (see `config.py`).
- Must satisfy `schemas.parse_manifest`: root object, `version` must be `1`, `items` array with valid entries.
- Media paths in items are resolved relative to `BASE_DIR` (repo root) per `schemas.py`.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| `Nustatyk BOT_TOKEN...` or similar | `.env` present, `BOT_TOKEN` non-empty, no stray quotes breaking the value |
| `Nustatyk ADMIN_CHAT_ID...` | Non-empty string that parses as `int`; `validate_config` rejects only `0` (negative ids exist for groups). For the usual setup, set **your user id** from @userinfobot or similar. |
| `Access denied. Admin only.` | The bot compares `update.effective_user.id` to `ADMIN_CHAT_ID`. Set `ADMIN_CHAT_ID` to **your user id** (e.g. from @userinfobot). Works in a **private** chat or in a **group** if you are that user. |
| `Turinio failas nerastas` | `data/content.json` exists and path matches `CONTENT_PATH` |
| Manifest error: empty `items` | `schemas.parse_manifest` requires a non-empty `items` array |
| `Content list is empty.` | Empty `manifest.items` at runtime (unexpected if content was loaded through `parse_manifest`) |
| `Could not read status or content. Check logs.` | Same sources as below: bad `state.json` shape, manifest/load errors on `/status`. |
| `Could not prepare content. Check logs.` / manifest errors | JSON syntax and schema: `version`, required fields per item type in `schemas.py` |
| `Send failed. Check logs.` | Media paths are resolved to **absolute** paths under `BASE_DIR` when the manifest loads (`schemas.parse_manifest`), not from process cwd. Also check Telegram API/network, rate limits, bad or oversized files, and logs for the real exception. |
| `Delivered but could not save progress...` | Telegram send succeeded but writing `data/state.json` failed (disk, permissions, etc.). Check logs; the next `/next` may deliver the same item again until state saves. |

## State file

- `data/state.json` is created on first successful delivery update. Do not hand-edit unless you understand `last_delivered_id` semantics (see [ARCHITECTURE.md](ARCHITECTURE.md)).
