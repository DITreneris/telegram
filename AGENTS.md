# AGENTS — 63 Telegram bot

This file is the **entry point** for people and for Cursor: where the project lives, how to run it, and which AI rules/skills apply.

## Purpose

Admin-only Telegram bot (MVP) that delivers queued items from `data/content.json` in order, with state in `data/state.json` (item types: text, photo, document, **poll**). Commands: `/start`, `/next`, `/status`.

**Scale:** the social curriculum is **large**—on the order of **~70+** rows in [web/public/posts.json](web/public/posts.json), each with a matching **`NN_Prompt_Anatomy.png`**, a linked quiz in [data/polls.json](data/polls.json), and (after sync) multiple manifest items per post (typically **photo → text → poll**). Post **sequence** in the bot queue is either optional [data/post_journey_order.json](data/post_journey_order.json) or greedy `topic_key` / theme interleaving—see [queue_manifest_sync.py](queue_manifest_sync.py) and [docs/QUEUE_SYNC.md](docs/QUEUE_SYNC.md#explicit-journey-order).

**“Agents” in this repo** means documented roles implemented via [Cursor project skills](.cursor/skills/) (optional invocation), not separate running processes.

## Content pipeline (do not get lost)

| Step | What |
|------|------|
| Author copy + image path | [web/public/posts.json](web/public/posts.json); PNG under [web/public/images/posts/](web/public/images/posts/) (and mirror [data/images/](data/images/) for local parity) |
| Author quizzes | [data/polls.json](data/polls.json) (`related_post_id` per post) |
| Web UI quiz payload (build) | [web/public/polls.json](web/public/polls.json) — synced from `data/polls.json` (see [web/package.json](web/package.json) `predev` / `prebuild`, [scripts/sync_polls_to_web.mjs](scripts/sync_polls_to_web.mjs)) |
| Optional curated bot order | [data/post_journey_order.json](data/post_journey_order.json) (`post_ids` permutation, exact match to all `posts.json` ids — **committed here** for a fixed Telegram deck; delete to fall back to greedy interleaving); regenerate starter: `python scripts/generate_post_journey_order.py` — see [docs/QUEUE_SYNC.md](docs/QUEUE_SYNC.md#explicit-journey-order) |
| Regenerate Telegram queue | `python scripts/sync_queue_from_posts.py` — default writes gitignored [data/content.generated.json](data/content.generated.json); **`--in-place`** updates [data/content.json](data/content.json) (what the bot loads) |
| Verify posts ↔ PNG ↔ polls | `python scripts/audit_posts_png_quizzes.py` (optional `--write-inventory docs/CONTENT_INVENTORY.md`) |

**Routine edits:** change `posts.json` / `polls.json`, then sync the manifest—**avoid hand-editing** `data/content.json` unless you are fixing an exceptional one-off.

**Which doc for which question:** build manifest → [docs/QUEUE_SYNC.md](docs/QUEUE_SYNC.md); post authoring → [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md); PNG/JSON coverage metrics → [docs/POST_IMAGES.md](docs/POST_IMAGES.md) + [docs/CONTENT_INVENTORY.md](docs/CONTENT_INVENTORY.md); planned **1–100** slots vs disk → [docs/POST_IMAGES_GAP_1_100.md](docs/POST_IMAGES_GAP_1_100.md).

## Where to look

| Area | Path |
|------|------|
| Documentation index | [docs/INDEX.md](docs/INDEX.md) |
| Archived / non-canonical docs | [docs/archive/README.md](docs/archive/README.md) |
| Doc management / versioning | [docs/VERSIONING.md](docs/VERSIONING.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| Architecture (incl. KISS principles) | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Run / env / troubleshooting | [docs/RUNBOOK.md](docs/RUNBOOK.md) |
| Env template | [.env.example](.env.example) |
| Bot entry + polling | [bot/main.py](bot/main.py) |
| Command handlers | [bot/handlers.py](bot/handlers.py) |
| Content queue logic | [orchestrator.py](orchestrator.py) |
| Manifest parsing | [schemas.py](schemas.py), [content_loader.py](content_loader.py) |
| Merge **posts + polls** → manifest dict | [queue_manifest_sync.py](queue_manifest_sync.py), CLI [scripts/sync_queue_from_posts.py](scripts/sync_queue_from_posts.py) |
| State file (load/save atomic) | [state_store.py](state_store.py) |
| Config / paths / optional `LOG_LEVEL` | [config.py](config.py) |
| Process entry | [run.py](run.py); Railway worker config [railway.toml](railway.toml) |
| Automated tests (pytest) | [tests/](tests/) — žr. [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests) |
| Social posts (Vite) + publish | [web/README.md](web/README.md), [web/public/posts.json](web/public/posts.json) |
| Quiz bank (source) | [data/polls.json](data/polls.json) |
| Quiz JSON for web build | [web/public/polls.json](web/public/polls.json) |
| Inventory audit (posts / PNG / polls) | [scripts/audit_posts_png_quizzes.py](scripts/audit_posts_png_quizzes.py), [docs/CONTENT_INVENTORY.md](docs/CONTENT_INVENTORY.md) |

## How to run

**Production queue bot (hosting):** [Railway](https://railway.com/) — single worker, `python run.py`, env vars like `.env.example`; see [docs/RUNBOOK.md](docs/RUNBOOK.md#hosting-the-queue-bot-railway). Web UI + publish stay on **Vercel** ([web/README.md](web/README.md)).

**Local:**

1. `python -m venv .venv` then activate (Windows: `.venv\Scripts\activate`).
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set `BOT_TOKEN`, `ADMIN_CHAT_ID`, and optionally `LOG_LEVEL` or scheduled posting (`ENABLE_SCHEDULED_POSTING`, `SCHEDULE_TZ`, `SCHEDULE_TARGET_CHAT_ID` — see [docs/RUNBOOK.md](docs/RUNBOOK.md)).
4. From repo root: `python run.py`

**Tests (dev):** `pip install -r requirements-dev.txt`, then from repo root `python -m pytest` (see [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests)).

## Quality assurance

- Prieš sujungiant esminius Python pakeitimus: `python -m pytest` iš repo šaknies (tas pats interpretatorius kaip `pip install -r requirements-dev.txt`).
- Prieš sujungiant pakeitimus po `api/`: iš repo šaknies `npm ci` ir `npm run check:api` (arba `npm run verify`) — žr. [docs/RUNBOOK.md](docs/RUNBOOK.md#api-typecheck).
- GitHub Actions **python** job after pytest runs `python scripts/audit_posts_png_quizzes.py` (fails on broken posts/PNG/polls alignment); žr. [docs/RUNBOOK.md](docs/RUNBOOK.md#quick-operator-rules).
- Keičiant `config.validate_config`, eilę, manifestą, būsenos įrašymą ar siuntimą — pridėkite ar atnaujinkite testus `tests/` (žr. esamus `test_*` failus).
- Dabartinė istorija: [CHANGELOG.md](CHANGELOG.md) (pvz. `[0.3.5]`).

**Socialinių postų kopijavimas (frontend):** `cd web`, `npm install`, `npm run dev`. **Vercel:** projekto šaknis turi būti **visa repozitorija**, jei naudojate Telegram publish (`vercel.json` + `api/`); šaknis **`web`** tinka tik jei publish nenaudojate. Įdiegti URL ir `/api/publish` pavyzdžiai: [web/README.md](web/README.md) (skiltis **Įdiegta (pavyzdiniai URL)**).

## Cursor assets

### Rules (`.cursor/rules/*.mdc`)

| Rule | When it applies |
|------|------------------|
| `project-core.mdc` | Always — secrets, minimal diffs, Python style, English user-facing bot text in Telegram |
| `python-bot.mdc` | Python files — python-telegram-bot patterns, admin gate, orchestration boundaries |
| `documentation.mdc` | `docs/**` and this file — keep [docs/INDEX.md](docs/INDEX.md) in sync |

### Skills (`.cursor/skills/`)

| Skill | Use when |
|-------|----------|
| [telegram-bot-coding](.cursor/skills/telegram-bot-coding/SKILL.md) | Editing bot Python: handlers, orchestrator, schemas, config, content loading |
| [document-qa](.cursor/skills/document-qa/SKILL.md) | Answering from project docs, updating the doc index, adding or restructuring documentation |
