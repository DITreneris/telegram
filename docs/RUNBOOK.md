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

## When the bot is running (local)

- **Expected:** the process **blocks** on long polling until you stop it (Ctrl+C). The console shows log lines at the configured `LOG_LEVEL` (default `INFO`).
- **Smoke check:** open a **private** chat with the bot (or the group where you use it), send `/start` or `/status` from the account whose **user id** matches `ADMIN_CHAT_ID`. You should get English replies; `/start` includes inline **Next** / **Status** buttons; `/status` prints item count, last delivered id, next id/type, and state `updated_at`. On startup the bot registers **Telegram command menu** entries (`/start`, `/next`, `/status`) for the **admin private chat** only (default scope is empty so strangers do not see those commands in the menu bar).
- **BotFather copy:** canonical **Description** and **About** strings for [@BotFather](https://t.me/BotFather) live in [bot/bot_copy.py](../bot/bot_copy.py) (`BOTFATHER_SHORT_DESCRIPTION`, `BOTFATHER_ABOUT`). The API cannot set them—paste manually when you change the wording.
- **Scheduled mode:** if `ENABLE_SCHEDULED_POSTING` is on, startup logs include `Scheduled posting enabled: 08:00, 08:30, 19:00, 19:30` with the IANA timezone key and target `chat_id`.
- **Do not run two processes** with the same `BOT_TOKEN` (second instance typically gets Telegram `Conflict` / “terminated by other getUpdates”).

## Hosting the queue bot (Railway)

**Decision:** the **Telegram queue bot** (`python run.py`, polling + optional `JobQueue`) is hosted on **[Railway](https://railway.com/)** as a single long-running worker. **Vercel** remains for the **static web app** + **`/api/publish`** only — it does not run this Python process.

**Why not Vercel for the bot:** serverless functions are not a substitute for a 24/7 polling process and in-repo scheduling.

### Railway setup (summary)

1. Connect the **GitHub** repo; create a **new service** from the repo (use **repository root** as the project root — same layout as local dev).
2. Treat the service as a **worker** (no public HTTP required for the bot). Start command is fixed in [`railway.toml`](../railway.toml): `python run.py`.
3. Set **Variables** to match production needs (at minimum `BOT_TOKEN`, `ADMIN_CHAT_ID`; optional schedule keys from the env table below — same names as `.env.example`).
4. Optional: set **`RAILPACK_PYTHON_VERSION=3.11`** on the service (or add a [`.python-version`](https://railpack.com/languages/python/) / `runtime.txt` file) so the runtime matches CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).
5. In the Railway service settings, keep **one replica** only (do not scale this service horizontally). Multiple instances share no distributed lock; two bots polling the same token cause Telegram `Conflict` errors.

### `data/state.json` on Railway

Railway’s container filesystem is **ephemeral**: redeploys and platform restarts can **reset or wipe** files under `data/` that are not in the image. **`data/state.json`** (queue cursor) may be **lost** after a deploy — the next delivery may not match what you expect until state is recreated. Mitigations when this becomes painful: add a **Railway volume** mounted at `data/` (if you use volumes), or move cursor storage to an external store (future work — not required for MVP if you accept occasional reset after deploy).

**Committed** `data/content.json` (and media paths under `data/images/` in the repo) are part of the deploy artifact and behave like a fresh clone each build.

### Cost / ops

Railway bills on **usage**; monitor the project dashboard. For lean operation, one small always-on worker is the target shape.

## Running tests

1. Install dev dependencies: `pip install -r requirements-dev.txt` (includes `pytest` and app requirements).
2. From the **repository root**, run tests with the **same interpreter** you used for `pip`: prefer `python -m pytest` (not only the bare `pytest` command), so the active environment is unambiguous.

Tests live under `tests/`; `pytest.ini` sets `pythonpath` so imports resolve from the repo root.

### API typecheck

Vercel serverless code under `api/` (e.g. `api/publish.ts`) is checked with TypeScript (no emit). From the **repository root** (Node **22.x**, same as [`.nvmrc`](../.nvmrc)):

1. `npm ci`
2. `npm run check:api` (alias: `npm run verify`)

**Full pre-push (mirrors CI):** `python -m pytest`, `python scripts/audit_posts_png_quizzes.py`, then `npm run check:api`, then `node scripts/sync_polls_to_web.mjs`, `cd web && npm ci && npm run build`.

**CI (GitHub):** On push/PR to `main`, [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs `python -m pytest` then `python scripts/audit_posts_png_quizzes.py` (**python** job), root `npm ci` + `npm run check:api` (**api_ts** job), and builds the web app (**web** job: `node scripts/sync_polls_to_web.mjs`, then `cd web && npm ci && npm run build`).

**Windows / multiple Python installs:** If `pytest` fails with `No module named pytest` or `python run.py` and tests use different versions, create and **activate** `.venv` (see **Setup** above), then `pip install -r requirements-dev.txt` and `python -m pytest` from the repo root inside that environment.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram bot token from BotFather |
| `ADMIN_CHAT_ID` | Yes | Your Telegram **user** id (same as [`.env.example`](../.env.example)); the bot compares it to `update.effective_user.id` for **authorization**. Messages are still sent to `update.effective_chat.id` (private chat or group where you run the command). |
| `LOG_LEVEL` | No | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` (default `INFO`; unknown values fall back to `INFO` with a warning) |
| `ENABLE_SCHEDULED_POSTING` | No | When `true` / `1` / `yes`, registers four daily queue sends at **08:00**, **08:30**, **19:00**, and **19:30** (see [ARCHITECTURE.md](ARCHITECTURE.md)). Default off. |
| `SCHEDULE_TZ` | No | IANA timezone for those times (default `Europe/Vilnius`). Invalid values fail at startup. |
| `SCHEDULE_TARGET_CHAT_ID` | No | Chat id for scheduled sends. If unset, uses `ADMIN_CHAT_ID` (fine for private DM with the bot). Use the **group** chat id if `/next` runs in a group and scheduled posts should go there too. |
| `SCHEDULE_NOTIFY_ON_FAILURE` | No | When `true` (default), a failed scheduled send **or** a successful send whose `state.json` write fails triggers a short **English** DM to the admin at `ADMIN_CHAT_ID`. Set `false` / `0` / `no` to disable and rely on logs only. |

If either required variable is missing or invalid at startup, `validate_config()` in `config.py` raises a clear error. When `ENABLE_SCHEDULED_POSTING` is on, `SCHEDULE_TZ` must be valid and `SCHEDULE_TARGET_CHAT_ID` (if set) must be a non-zero integer.

See [`.env.example`](../.env.example) for commented optional keys (HTTP publish, etc.).

## Content manifest

- Default path: `data/content.json` (see `config.py`).
- Must satisfy `schemas.parse_manifest`: root object, `version` must be `1`, `items` array with valid entries.
- Media paths in items are resolved relative to `BASE_DIR` (repo root) per `schemas.py`.
- Optional `caption` on `photo` / `document` items: at most **140** characters when set. For image plus long copy (hook then full text), see [ARCHITECTURE.md](ARCHITECTURE.md) (section **Image or document plus long copy**).
- **`poll`** items: Telegram **quiz** polls (`question`, `options`, `correct_option_id`). Optional **`theme_note`** on a poll is sent as a **follow-up text message** in the same chat after the quiz (debrief). To rebuild the queue from `web/public/posts.json` + `data/polls.json`, see [QUEUE_SYNC.md](QUEUE_SYNC.md).
- Regenerating `data/content.json` (e.g. `python scripts/sync_queue_from_posts.py --in-place`) **reorders** manifest items when post journey ordering changes. `data/state.json`’s `last_delivered_id` still points at the same id string, but the **next** item in sequence may differ from before. Either accept the new sequence or reset/adjust `last_delivered_id` after a sync (see [ARCHITECTURE.md](ARCHITECTURE.md)).

## Local bot vs web publish (Vercel)

Running **`python run.py`** starts the **queue bot**: it reads `data/content.json`, advances `data/state.json` on successful `/next` deliveries (and on successful **scheduled** sends when `ENABLE_SCHEDULED_POSTING` is enabled), and supports text, photo, document, and **poll** items per the manifest.

The **social copy UI** can publish post text (and, when the post has `image`, an optional same-origin photo URL) via **`POST /api/publish`** (see [`web/README.md`](../web/README.md)). That path uses the same bot token style on the server but is **separate** from the queue: it does not update `last_delivered_id`. For a full comparison, see [ARCHITECTURE.md](ARCHITECTURE.md) (section **Telegram delivery paths**).

### Quick operator rules

No new databases or services—just the existing bot, web UI, and files under `data/` / `web/public/`.

- **Curriculum delivery in order** → use the **bot** (`/next` or scheduled jobs). Expect `data/state.json` to move only on successful bot sends.
- **One-off post to the channel from the browser** → use **Publikuoti į Telegram** in the web UI. That does **not** advance the queue; plan `/next` separately if you also need manifest progress.
- **After editing** `web/public/posts.json`, **`data/polls.json`**, or files under `web/public/images/posts/` / `data/images/`: run `python scripts/audit_posts_png_quizzes.py` locally (CI runs it on every push/PR). If you use inventory docs, re-run with `--write-inventory docs/CONTENT_INVENTORY.md`.
- **Before relying on web publish in production:** Vercel **Production** env must include publish + bot vars (see [`web/README.md`](../web/README.md)); if **Deployment Protection** is on, configure bypass or rely on the UI’s small-image **base64** path.

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
| `Delivered but could not save progress...` | Telegram send succeeded but writing `data/state.json` failed (disk, permissions, etc.). Check logs; the same queue item may be sent again on the next `/next`, scheduled tick, or both until state saves. For scheduled sends, this message is DM’d to the admin when `SCHEDULE_NOTIFY_ON_FAILURE` is on (default). |
| Published from the web UI but `/next` did not advance the queue | **Expected.** The Vercel/serverless publish endpoint does not call `Orchestrator` or write `state.json`. Use `/next` in the bot for manifest queue progress. See [ARCHITECTURE.md](ARCHITECTURE.md) (**Telegram delivery paths**). |
| Publish photo: `Could not fetch image (HTTP 401)` | **Vercel Deployment Protection** blocks serverless `fetch` to your static files. The web UI sends small images (≤~3MB) as **base64** automatically; for larger files set env **`VERCEL_AUTOMATION_BYPASS_SECRET`** (Protection Bypass for Automation) or shrink the asset. See [`web/README.md`](../web/README.md). |
| Nothing scheduled appears in the **group** where I run `/next`, but manual `/next` works | **`/next` sends to `effective_chat`** (the group). **Scheduled** sends go to `SCHEDULE_TARGET_CHAT_ID` if set; if the variable is **unset**, `validate_config()` sets the in-memory target to **`ADMIN_CHAT_ID`** (private DM with the bot — same as manual `/next` in DMs, but **not** the group). Set `SCHEDULE_TARGET_CHAT_ID` to the group’s numeric chat id so scheduled posts match `/next` in that group. |
| DM: `Scheduled delivery failed: id=…, type=…` | Telegram rejected that queued item (permissions, limits, or chat restrictions). Check full traceback in logs (`scheduled_delivery: telegram send error` or similar). Confirm the bot can post polls/messages in the **scheduled** target chat. |
| Want failures only in logs, not Telegram | Set `SCHEDULE_NOTIFY_ON_FAILURE=false`. |

## State file

- `data/state.json` is created on first successful delivery update. Do not hand-edit unless you understand `last_delivered_id` semantics (see [ARCHITECTURE.md](ARCHITECTURE.md)).
