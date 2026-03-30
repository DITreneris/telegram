# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for **released** tags when you publish versions; until then, use `[Unreleased]` and date-stamped notes as needed.

Section order within each release: **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed**, **Security**. Newest release at the top.

## [Unreleased]

## [0.3.6] - 2026-04-02

### Added

- Web socialinių postų UI: paveikslėlio atsisiuntimas („Atsisiųsti paveikslėlį“), teksto redagavimas ir atkūrimas tik naršyklės sesijoje (`sessionStorage`); „Kopijuoti“ ir „Publikuoti į Telegram“ naudoja pataisytą tekstą ([web/src/main.ts](web/src/main.ts), [web/src/style.css](web/src/style.css)).

### Changed

- [web/README.md](web/README.md): dokumentuotas sesijos redagavimas ir paveikslėlio atsisiuntimas (skiltis **Turinys**).

## [0.3.5] - 2026-04-01

### Added

- [tests/test_handlers_next.py](tests/test_handlers_next.py): `test_cmd_next_long_text_sends_multiple_messages_then_records_once` — ilgas `text` `/next` siunčiamas keliais `sendMessage` kvietimais.

### Fixed

- [bot/handlers.py](bot/handlers.py): `text` turinys skaidomas po 4096 simbolių (`split_telegram_text_chunks`, `MAX_MESSAGE_CHARS`), sinchronuojant su [api/publish.ts](api/publish.ts); ilgi `/next` įrašai nebekrenta dėl Telegram `sendMessage` limito.

### Changed

- [.env.example](.env.example): aiškiau, kad `ADMIN_CHAT_ID` yra naudotojo skaitinis id, ne grupės pokalbio id.
- [web/README.md](web/README.md): Node 22 (`.nvmrc` / `engines`) vs lokalaus Node 20 `EBADENGINE` pastaba.

## [0.3.4] - 2026-03-31

### Added

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): section **Telegram delivery paths** (queue bot vs `api/publish` web UI, no shared `state.json`; mermaid diagram).
- [docs/RUNBOOK.md](docs/RUNBOOK.md): **Local bot vs web publish (Vercel)** and troubleshooting row when the web publish does not advance `/next` queue.
- [docs/INDEX.md](docs/INDEX.md): updated summaries and Last reviewed for architecture and runbook.
- [web/README.md](web/README.md): **Įdiegta (pavyzdiniai URL)** — production ir papildomi Vercel hostname’ai, `/api/publish` pilnas URL, `VITE_PUBLISH_API_URL` pastaba.

### Changed

- [AGENTS.md](AGENTS.md): Vercel šaknies nurodymai sutapatinti su `web/README` (visa repo su publish; tik `web` be publish); nuoroda į deployment URL skiltį.
- [package.json](package.json) ir [web/package.json](web/package.json): `engines.node` pakeistas iš `>=20.19.0` į `22.x` (sutampa su [.nvmrc](.nvmrc); mažina Vercel CLI įspėjimą apie automatinį major Node atnaujinimą; Vite 8 reikalavimas ≥20.19 išlieka tenkinamas).

## [0.3.3] - 2026-03-30

### Added

- Root [vercel.json](vercel.json): Vercel builds from `web/` (`npm ci`, `npm run build`) and publishes `web/dist` when the connected Git root is the whole repository; `framework: null` selects the **Other** preset so Vercel does not treat the repo as Python.
- Root [package.json](package.json) and [.nvmrc](.nvmrc) (`22`): pin Node for Vercel (Vite 8 requires Node **≥20.19**); [web/package.json](web/package.json) `engines` aligned.
- Telegram **publish from the social copy UI**: [web/src/main.ts](web/src/main.ts) adds **Publikuoti į Telegram** per post; calls `POST /api/publish` with `Authorization: Bearer` (prompt + [sessionStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage) on first use, or optional `VITE_PUBLISH_BEARER_TOKEN`; optional `VITE_PUBLISH_API_URL`). Long text is split server-side to respect Telegram’s 4096-character limit.
- Vercel serverless [api/publish.ts](api/publish.ts): validates bearer, sends `sendMessage` via Telegram Bot API using env `TELEGRAM_BOT_TOKEN` or `BOT_TOKEN`, target `TELEGRAM_PUBLISH_CHAT_ID` or `PUBLISH_CHAT_ID`, and `PUBLISH_BEARER_TOKEN`. Root [package.json](package.json) dependency `@vercel/node` for the function runtime.
- [web/src/vite-env.d.ts](web/src/vite-env.d.ts): `ImportMetaEnv` for optional publish-related `VITE_*` variables.

### Changed

- [vercel.json](vercel.json): `installCommand` is `npm ci && cd web && npm ci` so root `api/` dependencies install alongside the Vite app.
- [web/README.md](web/README.md): Vercel — use **repository root** as the project root when using Telegram publish (`vercel.json` + `api/`); **Publikuoti į Telegram** section documents required env vars and limitations (text-only; images from `posts.json` not sent).
- [web/src/style.css](web/src/style.css): `.card-actions` gap/wrap; `.btn-telegram` styles.
- [`.gitignore`](.gitignore): ignore root `node_modules/` if present.
- [web/public/posts.json](web/public/posts.json): each LinkedIn-style post opens with a thematic emoji plus 2–3 more varied emojis at key beats (3–4 per post total; existing ❌/✅ examples kept where present).

## [0.3.2] - 2026-03-30

### Added

- Content manifest: optional `caption` on `photo` / `document` items is validated to at most **140** characters when set ([schemas.py](schemas.py) `MAX_CAPTION_CHARS`, `parse_manifest`); [tests/test_schemas.py](tests/test_schemas.py) covers at-limit and over-limit cases.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): section **Image or document plus long copy** (Telegram caption vs message limits, two consecutive queue items for hook + full post, 140-char hook intended for future X/Twitter reuse, full text + CTA oriented to Telegram); **Data** / **Marry** bullets and modules table note the caption rule.
- [docs/RUNBOOK.md](docs/RUNBOOK.md): content manifest note on caption length and pointer to the architecture section.

## [0.3.1] - 2026-03-29

### Changed

- Admin gate in [bot/handlers.py](bot/handlers.py) uses `update.effective_user.id` vs `ADMIN_CHAT_ID` (still the admin’s Telegram **user** id); delivery remains `update.effective_chat.id`. [docs/RUNBOOK.md](docs/RUNBOOK.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [.cursor/rules/python-bot.mdc](.cursor/rules/python-bot.mdc).

### Fixed

- [bot/handlers.py](bot/handlers.py): after a successful send, `record_delivered` is wrapped in `try/except`; persistence failures are logged and the user gets a clear English message; narrowed `except` clauses for `/next` and `/status` (`TelegramError`, `OSError`, `ValueError`, `FileNotFoundError`, with `Exception` fallback and distinct log messages).

### Added

- [tests/test_handlers_next.py](tests/test_handlers_next.py): `test_cmd_next_record_failure_after_send`, `test_cmd_next_admin_in_group`; mocks set `effective_user` for the new gate.

## [0.3.0] - 2026-03-29

### Added

- [docs/archive/](docs/archive/) for non-canonical material; [docs/archive/README.md](docs/archive/README.md). [docs/bot_concept_notes.txt](docs/bot_concept_notes.txt) is a short compatibility pointer; full notes: [docs/archive/bot_concept_notes.txt](docs/archive/bot_concept_notes.txt).
- [tests/test_handlers_next.py](tests/test_handlers_next.py): contract-style tests for `/next` (`peek_next_item` before send, `record_delivered` only after success; no record on peek/send failure; non-admin skips orchestrator).

### Changed

- Root `30_posts.txt` moved to [docs/archive/30_posts.txt](docs/archive/30_posts.txt) (legacy JSON snapshot). Canonical social copy: [web/public/posts.json](web/public/posts.json). [docs/INDEX.md](docs/INDEX.md) documents what each `.txt` in the repo is for; [web/README.md](web/README.md) points to the archive snapshot.
- [web/public/posts.json](web/public/posts.json): LinkedIn-oriented order — array cycles 10 themes so consecutive posts do not repeat the same `theme`; days 1–10 / 11–20 / 21–30 use copy variants (`option` 1 / 2 / 3). `id` values renumbered 1–30 to match the social copy UI ([web/src/main.ts](web/src/main.ts)).
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): **Marry — long-lived core** (peek does not write, record after success, manifest via `parse_manifest`, state via `state_store`, startup manifest load); test file pointers. **KISS** section (thin handlers, single `/next` lock, EN Telegram without i18n, admin gate, checklist).
- Telegram bot user-facing strings (handlers, `/status` summary, sample `data/content.json`) are **English**; Cursor rules and [AGENTS.md](AGENTS.md) updated. Startup `validate_config` messages stay Lithuanian.
- [AGENTS.md](AGENTS.md): „Where to look“ extended (`state_store`, `tests/`, `LOG_LEVEL`, [docs/archive/README.md](docs/archive/README.md)); **Quality assurance** section; optional `LOG_LEVEL` in run instructions.
- [docs/VERSIONING.md](docs/VERSIONING.md): index rules include `docs/archive/`; changelog workflow clarified (`[Unreleased]` vs version section).
- [`.gitignore`](.gitignore): `.pytest_cache/`, `web/node_modules/`, `web/dist/`.
- Cursor: [.cursor/rules/python-bot.mdc](.cursor/rules/python-bot.mdc), [.cursor/rules/project-core.mdc](.cursor/rules/project-core.mdc), [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc); skills [.cursor/skills/telegram-bot-coding/SKILL.md](.cursor/skills/telegram-bot-coding/SKILL.md), [.cursor/skills/document-qa/SKILL.md](.cursor/skills/document-qa/SKILL.md) — `pytest` / QA and changelog references aligned with the repo.

## [0.2.0] - 2026-03-29

### Added

- Vienetiniai testai: [tests/test_state_store.py](tests/test_state_store.py), [tests/test_content_loader.py](tests/test_content_loader.py), [tests/test_config_validate.py](tests/test_config_validate.py) (`validate_config` su `importlib.reload`).
- [docs/bot_concept_notes.txt](docs/bot_concept_notes.txt) — istoriniai / alternatyvios architektūros užrašai (ne kanonas); ankstesnis `bot_concetp.txt` pašalintas.
- Neprivalomas `LOG_LEVEL` (`DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL`): `resolve_log_level()` [config.py](config.py), naudojama [bot/main.py](bot/main.py); netinkama reikšmė → `INFO` su `UserWarning`. [`.env.example`](.env.example) ir [docs/RUNBOOK.md](docs/RUNBOOK.md).
- Komentuota „Ateičiai“ sekcija [`.env.example`](.env.example) (`PUBLISH_CHAT_ID`, `ENABLE_SCHEDULED_POSTING`) — kol kas neskaitoma kode.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): išplėstas „Future expansion“ (scheduler, target chat, dublikatų apsauga, feature flag’ai, manifest vs „dienų“ ciklas).
- Vite frontend [web/](web/) — socialinių postų peržiūra ir vieno mygtuko kopijavimas; duomenys [web/public/posts.json](web/public/posts.json) (pradinė sinchronizacija su repo šaknies `30_posts.txt`, vėliau perkeltas į [docs/archive/30_posts.txt](docs/archive/30_posts.txt) nuo 0.3.0); LT sąsaja; Vercel: projekto šaknis `web` (žr. [web/README.md](web/README.md)).
- `pytest` suite under `tests/` with [requirements-dev.txt](requirements-dev.txt) and [pytest.ini](pytest.ini); tests for `schemas.parse_manifest`, orchestrator queue/state on disk, ir [tests/test_config_log_level.py](tests/test_config_log_level.py) (`resolve_log_level`).
- Orchestrator testas `test_peek_without_record_keeps_state` (būsena nesikeičia be `record_delivered`).
- Application logging: `logging.basicConfig` in [bot/main.py](bot/main.py); `logger.exception` in [bot/handlers.py](bot/handlers.py) when handlers fail.
- Root [README.md](README.md) (short overview; links to AGENTS and RUNBOOK).

### Changed

- [docs/RUNBOOK.md](docs/RUNBOOK.md): trikčių lentelė — `Siuntimas nepavyko` (absoliutūs keliai, API/tinklas), `ADMIN_CHAT_ID` / privatūs vs grupiniai pokalbiai; env lentelė aiškesnė dėl `effective_chat.id`.
- Eilė: `last_delivered_id` atnaujinamas tik po sėkmingo siuntimo (`peek_next_item` + `record_delivered`); `/next` naudoja `asyncio.Lock`.
- `ADMIN_CHAT_ID` nustatomas ir tikrinamas tik `validate_config()` metu (aiškios LT klaidos, `int` parse, ne 0).
- Centralizuotas PTB `add_error_handler` ([bot/main.py](bot/main.py)); handlerių klaidų atsakymai naudotojui be vidinių detalių.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): eilės semantika (`peek_next_item` / `record_delivered`).
- [docs/RUNBOOK.md](docs/RUNBOOK.md): added **Running tests** (dev install + `pytest`).
- [AGENTS.md](AGENTS.md): dev tests one-liner with anchor to RUNBOOK.
- [AGENTS.md](AGENTS.md): „Where to look“ ir **How to run** papildyti Vite socialinių postų įrankiu (`web/`).
- [docs/INDEX.md](docs/INDEX.md): RUNBOOK row summary now includes tests.

### Fixed

- [bot/handlers.py](bot/handlers.py): `_send_item` nepalieka „tylaus“ išėjimo nežinomam tipui (`RuntimeError`).

## [0.1.0] - 2026-03-29

### Added

- Telegram bot MVP (admin-only `/start`, `/next`, `/status`, content queue from `data/content.json`).
- `AGENTS.md`, [docs/INDEX.md](docs/INDEX.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/RUNBOOK.md](docs/RUNBOOK.md).
- Cursor project rules (`.cursor/rules/`) and skills (`.cursor/skills/telegram-bot-coding`, `document-qa`).
