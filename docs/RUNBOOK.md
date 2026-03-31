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
| `ENABLE_SCHEDULED_POSTING` | No | When `true` / `1` / `yes`, registers two daily queue sends at **08:00** and **19:00** (see [ARCHITECTURE.md](ARCHITECTURE.md)). Default off. |
| `SCHEDULE_TZ` | No | IANA timezone for those times (default `Europe/Vilnius`). Invalid values fail at startup. |
| `SCHEDULE_TARGET_CHAT_ID` | No | Chat id for scheduled sends. If unset, uses `ADMIN_CHAT_ID` (fine for private DM with the bot). Use the **group** chat id if `/next` runs in a group and scheduled posts should go there too. |

If either required variable is missing or invalid at startup, `validate_config()` in `config.py` raises a clear error. When `ENABLE_SCHEDULED_POSTING` is on, `SCHEDULE_TZ` must be valid and `SCHEDULE_TARGET_CHAT_ID` (if set) must be a non-zero integer.

See [`.env.example`](../.env.example) for commented optional keys (HTTP publish, etc.).

## Content manifest

- Default path: `data/content.json` (see `config.py`).
- Must satisfy `schemas.parse_manifest`: root object, `version` must be `1`, `items` array with valid entries.
- Media paths in items are resolved relative to `BASE_DIR` (repo root) per `schemas.py`.
- Optional `caption` on `photo` / `document` items: at most **140** characters when set. For image plus long copy (hook then full text), see [ARCHITECTURE.md](ARCHITECTURE.md) (section **Image or document plus long copy**).

## Local bot vs web publish (Vercel)

Running **`python run.py`** starts the **queue bot**: it reads `data/content.json`, advances `data/state.json` on successful `/next` deliveries (and on successful **scheduled** sends when `ENABLE_SCHEDULED_POSTING` is enabled), and supports text, photo, and document items per the manifest.

The **social copy UI** can publish post text (and, when the post has `image`, an optional same-origin photo URL) via **`POST /api/publish`** (see [`web/README.md`](../web/README.md)). That path uses the same bot token style on the server but is **separate** from the queue: it does not update `last_delivered_id`. For a full comparison, see [ARCHITECTURE.md](ARCHITECTURE.md) (section **Telegram delivery paths**).

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
| Published from the web UI but `/next` did not advance the queue | **Expected.** The Vercel/serverless publish endpoint does not call `Orchestrator` or write `state.json`. Use `/next` in the bot for manifest queue progress. See [ARCHITECTURE.md](ARCHITECTURE.md) (**Telegram delivery paths**). |
| Publish photo: `Could not fetch image (HTTP 401)` | **Vercel Deployment Protection** blocks serverless `fetch` to your static files. The web UI sends small images (≤~3MB) as **base64** automatically; for larger files set env **`VERCEL_AUTOMATION_BYPASS_SECRET`** (Protection Bypass for Automation) or shrink the asset. See [`web/README.md`](../web/README.md). |

## State file

- `data/state.json` is created on first successful delivery update. Do not hand-edit unless you understand `last_delivered_id` semantics (see [ARCHITECTURE.md](ARCHITECTURE.md)).
