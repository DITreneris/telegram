# Golden standard (regression barrier)

This document defines what **must stay true** for this repository. Treat it as the human-readable layer on top of CI: if a change breaks these rules, fix the change or update tests and this file together.

**Related:** [RUNBOOK.md](RUNBOOK.md) (commands), [ARCHITECTURE.md](ARCHITECTURE.md) (contracts), [AGENTS.md](../AGENTS.md) (entry point).

---

## 1. Automated gate (must pass before merge)

These steps mirror [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). A PR is not “green” unless all of them succeed.

| Step | Command | Notes |
|------|---------|--------|
| Python tests | `pip install -r requirements-dev.txt` then `python -m pytest` | From repo root; `pytest.ini` sets `pythonpath` and `testpaths`. |
| Content alignment audit | `python scripts/audit_posts_png_quizzes.py` | Fails on broken `posts.json` ↔ PNG ↔ `polls.json` alignment. |
| API TypeScript | `npm ci` then `npm run check:api` | Root `package-lock.json`; Node **22.x** (see `.nvmrc`). |
| Web build | `node scripts/sync_polls_to_web.mjs` then `cd web && npm ci && npm run build` | Ensures synced polls + Vite build. |

**Optional local “full mirror”** (see [RUNBOOK.md](RUNBOOK.md#running-tests)): run the rows above in order after substantive changes.

---

## 2. Architectural invariants (do not regress)

These are the **long-lived contracts** from [ARCHITECTURE.md](ARCHITECTURE.md). Breaking them without an explicit design change and test updates is a regression.

### Queue and state

- **`peek_next_item`** never persists state; it only reads manifest + `state.json`.
- **`record_delivered`** runs **only after** a successful Telegram send (`/next` and scheduled jobs share this rule).
- Failed send or failed peek must **not** advance `last_delivered_id`.
- State is read/written only through **`state_store.py`** (`load`, `save_atomic`, `default_state`); handlers must not hand-edit `data/state.json`.
- **One send implementation:** `send_content_item` in `bot/handlers.py` for both `/next` and `run_scheduled_delivery`.
- **Serialization:** shared `asyncio.Lock` around peek → send → record for `/next` and scheduled delivery.

### Manifest (`schemas.parse_manifest`)

- Root manifest `version` must be **`1`** (bumping version is a deliberate contract change).
- Item `id` values must be **unique** within the manifest.
- Media `path` values resolve only **under** `BASE_DIR` / `base_dir` after load.
- Optional `caption` on `photo` / `document`: at most **`MAX_CAPTION_CHARS` (140)** when set.
- **Poll** items: quiz shape per `schemas.py` (`MAX_POLL_QUESTION_CHARS`, `MAX_POLL_OPTION_CHARS`, option count bounds).
- Long **text** and poll **`theme_note`**: split for Telegram **`MAX_MESSAGE_CHARS` (4096)** in handlers (`split_telegram_text_chunks`).

### Bot behavior

- **Admin-only** commands: every privileged path goes through the same admin check (`effective_user.id` vs `ADMIN_CHAT_ID`).
- **User-facing Telegram text** is **English** (replies, scheduled failure notices to admin when applicable).
- **Startup:** invalid `data/content.json` must **fail fast** at bot startup (manifest load before polling).

### Operations

- **One** long-running process per `BOT_TOKEN` (no horizontal scale of the queue worker without a new locking story).
- **Secrets:** never commit `.env`, real `BOT_TOKEN`, or chat IDs; use [`.env.example`](../.env.example) only as the template.

---

## 3. Python and repo conventions

- **`from __future__ import annotations`**, type hints, **`pathlib.Path`** for filesystem paths where the codebase already does.
- **Smallest diff** that solves the task; no unrelated refactors in the same change.
- **`config.validate_config()`** is the single place for required env validation at startup; extend tests in `tests/test_config_validate.py` (and related) when behavior changes.

---

## 4. Test map (what guards what)

When you touch an area, run **`python -m pytest`**; prefer adding or extending tests in the matching file.

| Area | Primary tests |
|------|----------------|
| Orchestrator / queue cursor | `tests/test_orchestrator.py` |
| Manifest parsing / limits | `tests/test_schemas.py` |
| JSON load / manifest integration | `tests/test_content_loader.py` |
| `state.json` atomic IO | `tests/test_state_store.py` |
| `/next` send + ordering (mocked) | `tests/test_handlers_next.py` |
| `/start` + inline Next/Status callbacks (mocked) | `tests/test_handlers_start_nav.py` |
| Scheduled jobs | `tests/test_handlers_scheduled.py` |
| Posts + polls → manifest sync | `tests/test_queue_manifest_sync.py` |
| Config / env validation | `tests/test_config_validate.py` |
| `LOG_LEVEL` | `tests/test_config_log_level.py` |

---

## 5. Content pipeline (curriculum scale)

Authoring and regeneration are documented in [AGENTS.md](../AGENTS.md) and [QUEUE_SYNC.md](QUEUE_SYNC.md). Golden rules:

- Prefer **`python scripts/sync_queue_from_posts.py`** (with or without `--in-place`) over hand-editing `data/content.json`.
- After edits to **`web/public/posts.json`**, **`data/polls.json`**, or post images under **`web/public/images/posts/`** / **`data/images/`**, run **`python scripts/audit_posts_png_quizzes.py`** locally (CI always runs it).
- Regenerating the manifest can **reorder** items; `last_delivered_id` may point at a different “next” item—operators must account for that (see [RUNBOOK.md](RUNBOOK.md#content-manifest)).

---

## 6. When to update this document

Update **`docs/golden_standard.md`** when you:

- add or remove a **CI job** or change its commands;
- introduce a **new invariant** (e.g. new item type, new state field, new env var required at startup);
- add a **new test file** that is part of the regression story.

Keep the **automated gate** table in §1 in sync with `.github/workflows/ci.yml`.
