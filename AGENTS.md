# AGENTS — 63 Telegram bot

This file is the **entry point** for people and for Cursor: where the project lives, how to run it, and which AI rules/skills apply.

## Purpose

Admin-only Telegram bot (MVP) that delivers queued items from `data/content.json` in order, with state in `data/state.json`. Commands: `/start`, `/next`, `/status`.

**“Agents” in this repo** means documented roles implemented via [Cursor project skills](.cursor/skills/) (optional invocation), not separate running processes.

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
| State file (load/save atomic) | [state_store.py](state_store.py) |
| Config / paths / optional `LOG_LEVEL` | [config.py](config.py) |
| Process entry | [run.py](run.py) |
| Automated tests (pytest) | [tests/](tests/) — žr. [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests) |
| Socialinių postų kopijavimas (Vite) | [web/README.md](web/README.md), [web/public/posts.json](web/public/posts.json) |

## How to run

1. `python -m venv .venv` then activate (Windows: `.venv\Scripts\activate`).
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set `BOT_TOKEN`, `ADMIN_CHAT_ID`, and optionally `LOG_LEVEL`.
4. From repo root: `python run.py`

**Tests (dev):** `pip install -r requirements-dev.txt`, then from repo root `pytest` (see [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests)).

## Quality assurance

- Prieš sujungiant esminius Python pakeitimus: `pytest` iš repo šaknies (tas pats interpretatorius kaip `pip install -r requirements-dev.txt`).
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
