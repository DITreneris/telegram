# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for **released** tags when you publish versions; until then, use `[Unreleased]` and date-stamped notes as needed.

Section order within each release: **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed**, **Security**. Newest release at the top.

## [Unreleased]

### Fixed

- **Scheduled queue ticks skipped silently:** APScheduler’s default **`misfire_grace_time` is 1 second**. If the asyncio loop starts the daily job more than 1s after the scheduled instant (common under **getUpdates** polling load), the run is **dropped** (`EVENT_JOB_MISSED`) and **`run_scheduled_delivery` never runs** — no `scheduled_delivery: sending` log. [`bot/main.py`](bot/main.py) now passes **`job_kwargs={"misfire_grace_time": 600}`** (10 minutes) to all four `JobQueue.run_daily` registrations. Docs: [`docs/RUNBOOK.md`](docs/RUNBOOK.md) troubleshooting table.

### Changed

- [bot/main.py](bot/main.py): set **`httpx`**, **`httpcore`**, **`apscheduler`**, and **`apscheduler.scheduler`** loggers to **WARNING**; re-apply before **`JobQueue.run_daily`** (registration spam) and again immediately before `run_polling`. **`INFO`** `Queue bot polling started (scheduled_posting=…, railway_git_sha=…)` before polling — on Railway, `railway_git_sha` is **`RAILWAY_GIT_COMMIT_SHA`** when set so deploy logs prove which Git revision is running (`n/a` locally). Detect duplicate **`getUpdates`** via **`_is_getupdates_conflict`** (raw `Conflict`, `ExceptionGroup` / `__cause__` wrappers, or API message text) so deploy logs show one operator **ERROR** line instead of a long traceback. Tests: [tests/test_main_error_handler.py](tests/test_main_error_handler.py). See [docs/RUNBOOK.md](docs/RUNBOOK.md) (single replica, no second process with the same token).
- [docs/RUNBOOK.md](docs/RUNBOOK.md): **Railway** — use startup **`railway_git_sha=`** in logs to confirm the container matches GitHub `main`; set **`BOT_TOKEN`**, **`ADMIN_CHAT_ID`**, and optional schedule keys as **service Variables** (`.env` is gitignored and not baked into deploy). **Redeploy** on a fixed deployment often rebuilds the **same Git commit** — if **Active** lags behind `main`, trigger a **new deploy from branch tip** (or **Railway CLI** / fresh service) rather than only **Redeploy** on the stale deployment card.
- [bot/bot_copy.py](bot/bot_copy.py): BotFather **About** (`BOTFATHER_ABOUT`) shortened to ≤120 characters, clearer admin/content-queue wording; single-line assignment; module note that BotFather paste is plain text only (not Python syntax).

### Added

- **Bot UX:** canonical English strings in [bot/bot_copy.py](bot/bot_copy.py) for `/start`, BotFather **Description** / **About** (paste manually), and `set_my_commands` labels. [bot/main.py](bot/main.py) `post_init`: empty default command scope; `/start`, `/next`, `/status` registered for `BotCommandScopeChat(ADMIN_CHAT_ID)` (admin private DM menu). [bot/handlers.py](bot/handlers.py): `/start` sends inline **Next** / **Status** (`callback_nav`) delegating to the same logic as slash commands. Tests: [tests/test_handlers_start_nav.py](tests/test_handlers_start_nav.py). Docs: [docs/RUNBOOK.md](docs/RUNBOOK.md), [AGENTS.md](AGENTS.md).

## [0.3.11] - 2026-04-07

### Added

- **Regression barrier:** [docs/golden_standard.md](docs/golden_standard.md) — CI commands mirroring [`.github/workflows/ci.yml`](.github/workflows/ci.yml), architectural invariants, test map, content pipeline rules (keep §1 in sync when CI or deploy changes). Linked from [AGENTS.md](AGENTS.md), [.cursor/rules](.cursor/rules), and project skills.
- **Railway hosting (queue bot):** [`railway.toml`](railway.toml) uses **`RAILPACK`** builder (not `NIXPACKS`, which is invalid on current Railway) and `startCommand = python run.py`. [docs/RUNBOOK.md](docs/RUNBOOK.md#hosting-the-queue-bot-railway) documents GitHub connect, env vars, optional **`RAILPACK_PYTHON_VERSION=3.11`**, **one replica**, and **`data/state.json` ephemeral** caveat on redeploy. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) **Production shape**; [AGENTS.md](AGENTS.md) **How to run**; [docs/INDEX.md](docs/INDEX.md).
- **GitHub Actions CI** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): on push/PR to `main`, **python** job runs `python -m pytest` then `python scripts/audit_posts_png_quizzes.py`; **api_ts** runs root `npm ci` + `npm run check:api` (Node 22, typecheck [`api/publish.ts`](api/publish.ts) et al.); **web** job syncs `polls.json` → `web/public` and `npm ci` / `npm run build` in `web/`. Documented in [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests), [API typecheck](docs/RUNBOOK.md#api-typecheck), and [Quick operator rules](docs/RUNBOOK.md#quick-operator-rules).
- Root [`package.json`](package.json) script **`verify`**: alias for `npm run check:api` (`tsc --project tsconfig.api.json`).
- **`scripts/audit_posts_png_quizzes.py`:** exits with code **1** on canonical integrity failures (duplicate post ids, id/slot/filename mismatch, PNG basename reused across posts, orphan or duplicate quiz `related_post_id`, missing image files, image only on `data/images` without `web/public/images/posts/` mirror). Still exits **0** for softer gaps (e.g. post without quiz, extra PNG without row). **GitHub Actions** [**python** job](.github/workflows/ci.yml) runs this after `pytest`. [docs/RUNBOOK.md](docs/RUNBOOK.md) **Quick operator rules** (bot vs web publish, when to audit, Vercel env note); [AGENTS.md](AGENTS.md) Quality assurance; [docs/INDEX.md](docs/INDEX.md).
- **Local checks (developer machine):** Same **python** job as CI: activate a venv with Python **3.11** (matches Actions), `pip install -r requirements-dev.txt`, then `python -m pytest` and `python scripts/audit_posts_png_quizzes.py` (exit **0** when posts / PNG / polls alignment is clean). Verified on **Windows** with `py -3.11 -m venv venv` (folder may be `.venv` or `venv`). Node/API and web build steps: [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests) (full pre-push).

- **Batch QA checklist** in [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md): after large `posts.json` / `polls.json` edits, run structural audit (`audit_posts_png_quizzes.py`), semantic heuristic audit (`audit_post_quiz_semantics.py`), then `sync_queue_from_posts.py --in-place` and `python -m pytest` (plus `theme` / `theme_note` / web `polls.json` sync when themes change). [docs/INDEX.md](docs/INDEX.md) EDUCATIONAL_POSTS row notes the checklist.
- **Curated Telegram post order:** optional committed [`data/post_journey_order.json`](data/post_journey_order.json) (`version` 1, `post_ids` — exact permutation of all post ids); [`queue_manifest_sync.py`](queue_manifest_sync.py) uses it when present, else [`order_posts_for_journey`](queue_manifest_sync.py). [`scripts/generate_post_journey_order.py`](scripts/generate_post_journey_order.py) writes a bucketed round-robin starter order. Tests in [`tests/test_queue_manifest_sync.py`](tests/test_queue_manifest_sync.py). Docs: [`docs/QUEUE_SYNC.md`](docs/QUEUE_SYNC.md#explicit-journey-order), [`AGENTS.md`](AGENTS.md), [`docs/INDEX.md`](docs/INDEX.md).
- **`scripts/audit_post_quiz_semantics.py`:** heuristic post ↔ quiz QA (generic stub fingerprint list, `theme_note` vs `theme`, Jaccard overlap on non-stub bodies); documented in [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md).
- **`scripts/restore_posts_png_aligned.py`:** reset `web/public/posts.json` `theme`/`content` (slots **31+**) to `SLOT_THEMES` + `PLANNED_THEME_BY_SLOT`, sync poll `theme_note`, run `apply_poll_lesson_patches.py` + `sync_queue_from_posts.py --in-place` (PNG slot headlines as source of truth).
- **`scripts/sync_posts_json_from_generated_manifest.py`:** copy `theme` + `content` from `data/content.generated.json` into `web/public/posts.json` by `related_post_id`; refresh `data/polls.json` `theme_note`; `--dry-run` / `--no-polls`.
- **`scripts/realign_polls_with_posts.py`:** after the above sync, update quiz questions for role-stack and other restored post ids.
- **`scripts/audit_posts_png_quizzes.py`:** audit `posts.json` vs `web/public/images/posts/` vs `data/polls.json` (A–I, 1:1 id/slot principle, quiz coverage); optional `--write-inventory docs/CONTENT_INVENTORY.md`.
- **`scripts/merge_posts_json_from_png.py`:** rebuild `web/public/posts.json` with one row per `NN_Prompt_Anatomy.png` on disk (`--dry-run` / `--write`); themes for new slots from `PLANNED_THEME_BY_SLOT` in `gen_post_images_gap_report.py` or `TODO` stub.
- **`scripts/fill_stub_posts_and_expand_polls.py`:** replace TODO stub bodies with English educational copy from resolved themes; ensure **`data/polls.json`** has **one poll per post** (template question for ids 11+; ids **1–10** keep original `hot_or_not` copy).
- **[docs/CONTENT_INVENTORY.md](docs/CONTENT_INVENTORY.md)** and [docs/INDEX.md](docs/INDEX.md) entry; [docs/POST_IMAGES.md](docs/POST_IMAGES.md) cross-links.
- **Scheduled delivery diagnostics:** [`bot/handlers.py`](bot/handlers.py) logs `scheduled_delivery: sending to chat_id=… item_id=… type=…` at INFO before each send; on send failure (before `record_delivered`), optional English DM to the admin at `ADMIN_CHAT_ID` with item id/type and error summary. Env `SCHEDULE_NOTIFY_ON_FAILURE` (default on) in [`config.py`](config.py), wired in [`bot/main.py`](bot/main.py); documented in [`.env.example`](.env.example). Docs: [`docs/RUNBOOK.md`](docs/RUNBOOK.md) (env table + troubleshooting: scheduled target vs `/next` group, failure DM), [`docs/INDEX.md`](docs/INDEX.md). Tests: [`tests/test_handlers_scheduled.py`](tests/test_handlers_scheduled.py), [`tests/test_config_validate.py`](tests/test_config_validate.py).
- **Web marketing UI:** [`web/src/main.ts`](web/src/main.ts) loads `/polls.json`, shows quiz blocks per `related_post_id`, optional `topic_key` badge, **search** (theme / content / topic_key), **sort** (file order, id, theme A–Z), **publish-state filter** (all / published / unpublished). Successful **Publikuoti į Telegram** records timestamp in **`localStorage`** (`socialPostsPublished`). Styles: [`web/src/style.css`](web/src/style.css).
- **Web UX polish:** initial **Kraunama…** loading state; **debounced** search (250 ms); preserve **edit mode** when changing filters; **toast** banner (`aria-live`) instead of blocking `alert` for publish / copy / download fallback; single delegated `change` / `input` / `click` handlers on `#app` (no duplicate listeners per repaint); Lithuanian strings for publish flow; richer **`img` `alt`** (`Įrašas #id — theme`). Styles: `.app-loading`, `.toast--success` / `.toast--error`.
- [`scripts/sync_polls_to_web.mjs`](scripts/sync_polls_to_web.mjs): copy [`data/polls.json`](data/polls.json) → `web/public/polls.json`. Wired in [`vercel.json`](vercel.json) `buildCommand` and [`web/package.json`](web/package.json) `predev` / `prebuild`. [`web/public/polls.json`](web/public/polls.json) gitignored.
- **Post-quiz debrief:** for manifest items with `type` **`poll`**, when `theme_note` is set, [`bot/handlers.py`](bot/handlers.py) `send_content_item` sends it via `send_message` after `send_poll` (chunks if needed). [`schemas.py`](schemas.py): `MAX_MESSAGE_CHARS` and validation so poll `theme_note` does not exceed Telegram message size.
- Tests: [`tests/test_schemas.py`](tests/test_schemas.py) (poll `theme_note` too long), [`tests/test_handlers_next.py`](tests/test_handlers_next.py) / [`tests/test_handlers_scheduled.py`](tests/test_handlers_scheduled.py) (poll + debrief).
- Optional **`topic_key`** on [`web/public/posts.json`](web/public/posts.json) rows (stable slug per curriculum idea); when omitted, merge uses normalized `theme` for grouping only.
- **`order_posts_for_journey`** / **`effective_topic_key`** in [`queue_manifest_sync.py`](queue_manifest_sync.py): interleave posts by `topic_key` before expanding each post to photo + text + polls (avoids back-to-back **different post ids** with the same topic when possible).
- [`scripts/backfill_post_topic_keys.py`](scripts/backfill_post_topic_keys.py): fill `topic_key` from known `theme` strings or slug fallback.
- Docs: [docs/QUEUE_SYNC.md](docs/QUEUE_SYNC.md), [docs/RUNBOOK.md](docs/RUNBOOK.md) (regenerate manifest vs `data/state.json` / `last_delivered_id`), [docs/INDEX.md](docs/INDEX.md).
- Tests: [`tests/test_queue_manifest_sync.py`](tests/test_queue_manifest_sync.py) (`topic_key` validation, journey ordering).
- [scripts/gen_post_images_gap_report.py](scripts/gen_post_images_gap_report.py) ir [docs/POST_IMAGES_GAP_1_100.md](docs/POST_IMAGES_GAP_1_100.md): planiniai slotai 1–100 (`NN_Prompt_Anatomy.png`) vs `web/public/images/posts/` — kiek trūksta, lentelė su temomis (`posts.json` + plano žodynas); `PLANNED_THEME_BY_SLOT` papildytas slotui **100**. [docs/INDEX.md](docs/INDEX.md); nuoroda iš [docs/POST_IMAGES.md](docs/POST_IMAGES.md).
- Queue manifest **poll** type (Telegram quiz): [schemas.py](schemas.py), [bot/handlers.py](bot/handlers.py) `send_poll`; optional manifest fields `related_post_id`, `theme_note`. Quiz bank [data/polls.json](data/polls.json); merge tool [queue_manifest_sync.py](queue_manifest_sync.py), CLI [scripts/sync_queue_from_posts.py](scripts/sync_queue_from_posts.py). Doc [docs/QUEUE_SYNC.md](docs/QUEUE_SYNC.md); [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md) cross-link; [docs/INDEX.md](docs/INDEX.md), [AGENTS.md](AGENTS.md). Tests: [tests/test_queue_manifest_sync.py](tests/test_queue_manifest_sync.py), extended schema/handler tests. Default generated output `data/content.generated.json` (gitignored); `--in-place` writes `data/content.json`.
- [docs/MISSING_POST_IMAGES.md](docs/MISSING_POST_IMAGES.md): lentelė trūkstamiems PNG (failas, post `id`, `theme`); generuoja [scripts/gen_missing_post_images_md.py](scripts/gen_missing_post_images_md.py). Nuorodos [docs/POST_IMAGES.md](docs/POST_IMAGES.md), [docs/INDEX.md](docs/INDEX.md).
- [docs/POST_IMAGES.md](docs/POST_IMAGES.md): image coverage summary (`posts.json` vs `web/public/images/posts/`); [scripts/audit_post_images.py](scripts/audit_post_images.py) prints missing PNG basenames. [docs/INDEX.md](docs/INDEX.md), [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md) cross-links.
- [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md): golden standard for educational social posts (KISS/Marry/Kill rubric, `posts.json`, Telegram limits, adaptation workflow); related Cursor skills: [.cursor/skills/document-qa/SKILL.md](.cursor/skills/document-qa/SKILL.md), [.cursor/skills/telegram-bot-coding/SKILL.md](.cursor/skills/telegram-bot-coding/SKILL.md). [docs/INDEX.md](docs/INDEX.md), [AGENTS.md](AGENTS.md) updated.
- Optional **scheduled queue delivery** via python-telegram-bot `JobQueue` (`ENABLE_SCHEDULED_POSTING`, `SCHEDULE_TZ`, optional `SCHEDULE_TARGET_CHAT_ID`): same peek → send → `record_delivered` flow as `/next` with shared `asyncio.Lock` ([`bot/main.py`](bot/main.py), [`bot/handlers.py`](bot/handlers.py)). See **Changed** for current daily run times.
- [`config.py`](config.py): schedule validation; [`requirements.txt`](requirements.txt): `python-telegram-bot[job-queue]`, `tzdata`.
- Tests: [`tests/test_handlers_scheduled.py`](tests/test_handlers_scheduled.py), config cases in [`tests/test_config_validate.py`](tests/test_config_validate.py).

### Changed

- **Cursor / entry docs:** [AGENTS.md](AGENTS.md) — CI summary (python + api_ts + web jobs), link to [docs/golden_standard.md](docs/golden_standard.md); changelog example version bump. [.cursor/rules/project-core.mdc](.cursor/rules/project-core.mdc) / [python-bot.mdc](.cursor/rules/python-bot.mdc): `python -m pytest`, audit script, `bot_data` keys (`schedule_target_chat_id`, `schedule_notify_on_failure`), `_next_lock`, global `error_handler`, Railway **RAILPACK** deploy note. [.cursor/skills/telegram-bot-coding/SKILL.md](.cursor/skills/telegram-bot-coding/SKILL.md) / [document-qa/SKILL.md](.cursor/skills/document-qa/SKILL.md): golden standard + deploy quick ref. [documentation.mdc](.cursor/rules/documentation.mdc): keep `golden_standard` §1 aligned with CI. [docs/INDEX.md](docs/INDEX.md) — `golden_standard.md` row, `ci.yml` in Related repo files.
- **Docs:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — global `error_handler`, resolved `schedule_target_chat_id` (default `ADMIN_CHAT_ID`), `split_telegram_text_chunks` / `MAX_MESSAGE_CHARS`, `_next_lock`; operator-facing vs Telegram English copy. [docs/RUNBOOK.md](docs/RUNBOOK.md) — **When the bot is running** (local verification, scheduled log line, duplicate-token warning); troubleshooting row clarified for default scheduled target vs group `/next`. [docs/INDEX.md](docs/INDEX.md) summaries updated.
- **Production (Railway):** Queue bot smoke-tested from **mobile Telegram**; **`/start`**, **`/next`**, **`/status`** work. **`JobQueue` scheduled posting** (`ENABLE_SCHEDULED_POSTING`, four daily slots) **still to be verified** in production (correct `SCHEDULE_TZ`, `SCHEDULE_TARGET_CHAT_ID` vs group DM, deploy logs at 08:00 / 08:30 / 19:00 / 19:30 local).

- **Pedagogical micro-pass (posts 33, 44, 49, 60):** [web/public/posts.json](web/public/posts.json) — extra problem/reframe sentences only (`theme` unchanged; [data/polls.json](data/polls.json) untouched). [docs/CONTENT_INVENTORY.md](docs/CONTENT_INVENTORY.md) refreshed (`python scripts/audit_posts_png_quizzes.py --write-inventory docs/CONTENT_INVENTORY.md`). [data/content.json](data/content.json) regenerated (`sync_queue_from_posts.py --in-place`).
- **Micro copy (less repetitive rhythm):** [web/public/posts.json](web/public/posts.json) hooks/closings/workflow labels varied for role-stack posts **32, 37, 41, 46, 51, 56, 71, 76, 81, 86, 93–99** (tool lines and URLs unchanged); framing lines added for **65, 70, 75**. [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md): note on varying role-stack hooks without changing stacks. [data/content.json](data/content.json) regenerated.
- **Post 62:** [web/public/posts.json](web/public/posts.json) theme + body updated (data vs system for insight; collect → structure → analyze → decide); matching quiz + `theme_note` in [data/polls.json](data/polls.json); queue regenerated.
- **Post 100:** [web/public/posts.json](web/public/posts.json) theme + body updated (thinking vs AI problem; pressure/constraints); matching quiz + `theme_note` in [data/polls.json](data/polls.json); queue regenerated.
- **Content sync from generated manifest:** [web/public/posts.json](web/public/posts.json) `theme`/`content` for 41 slots (32–99 except 62/100) aligned from [data/content.generated.json](data/content.generated.json); [data/polls.json](data/polls.json) `theme_note` + questions via [scripts/realign_polls_with_posts.py](scripts/realign_polls_with_posts.py); [data/content.json](data/content.json) regenerated (`sync_queue_from_posts.py --in-place`); [web/public/polls.json](web/public/polls.json) via [scripts/sync_polls_to_web.mjs](scripts/sync_polls_to_web.mjs). [scripts/realign_polls_with_posts.py](scripts/realign_polls_with_posts.py): `ROLE_STACK_IDS` includes **66** for future Data Analyst stack rows.
- **Documentation / agent onboarding:** [AGENTS.md](AGENTS.md) adds **Content pipeline** (posts, `polls.json`, web `polls.json` sync, `sync_queue_from_posts.py`, audit); **Where to look** extended with `queue_manifest_sync.py`, quiz paths, inventory script. [docs/INDEX.md](docs/INDEX.md): clearer doc summaries (actual coverage vs 1–100 plan), expanded **Related repo files**. [.cursor/rules](.cursor/rules): `project-core.mdc` (social content + manifest scale), `documentation.mdc` (index alignment, no legacy 30-post counts), `python-bot.mdc` (`poll` + `theme_note`). Skills: [telegram-bot-coding](.cursor/skills/telegram-bot-coding/SKILL.md), [document-qa](.cursor/skills/document-qa/SKILL.md).
- **[data/polls.json](data/polls.json):** `poll_post_031_structure` question/options aligned with post **31** (image-tool job map).
- **[web/public/posts.json](web/public/posts.json) / PNG deck (source of truth):** **74** rows—one per `NN_Prompt_Anatomy.png` on disk (`id` = slot, canonical `/images/posts/…`); same **74** basenames under `web/public/images/posts/` and `data/images/`. **`data/polls.json`:** one quiz per `related_post_id`. Canonical loop is aligned (no missing PNG refs, no orphan web PNGs vs JSON—verify with `python scripts/audit_posts_png_quizzes.py`; optional `--write-inventory docs/CONTENT_INVENTORY.md`). After content changes, regenerate queue: `python scripts/sync_queue_from_posts.py --in-place`. Stub/theme workflows: [`scripts/fill_stub_posts_and_expand_polls.py`](scripts/fill_stub_posts_and_expand_polls.py), [docs/EDUCATIONAL_POSTS.md](docs/EDUCATIONAL_POSTS.md). *(Supersedes earlier Unreleased note that slots 31 and 100 used temporary PNG copies of other slots.)*
- **[data/polls.json](data/polls.json):** **74** quiz rows—one `related_post_id` per post; **1–10** keep `poll_post_001_hot_or_not` … `poll_post_010_hot_or_not`; **11+** use `poll_post_NNN_structure` template. Poll bank initially shipped with **10** rows; expanded to full deck coverage.
- **Scheduled posting:** [`bot/main.py`](bot/main.py) registers **four** `run_daily` callbacks to `run_scheduled_delivery` instead of two: **`scheduled_morning_1`** 08:00, **`scheduled_morning_2`** 08:30, **`scheduled_evening_1`** 19:00, **`scheduled_evening_2`** 19:30 (all in `SCHEDULE_TZ`, default `Europe/Vilnius`). Previously: 08:00 and 19:00 only. Docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/RUNBOOK.md](docs/RUNBOOK.md); [`.env.example`](.env.example).

- **Docs:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) **Data** section documents manifest `poll` type and key fields; [AGENTS.md](AGENTS.md) Purpose lists item types; [docs/RUNBOOK.md](docs/RUNBOOK.md) **Running tests** recommends `python -m pytest` and notes Windows / multiple Python + `.venv`.
- **Handlers:** [`bot/handlers.py`](bot/handlers.py) imports `MAX_MESSAGE_CHARS` from [`schemas.py`](schemas.py) (single source of truth; tests import the constant from `schemas`).

- **[data/content.json](data/content.json):** regenerated with `python scripts/sync_queue_from_posts.py --in-place` after expanding the poll bank (more `poll` items interleaved per post).
- **Queue manifest build**: post order in `build_manifest_dict` is no longer strictly numeric `id` sort; regenerate [`data/content.json`](data/content.json) with `python scripts/sync_queue_from_posts.py --in-place` after changing posts or ordering logic. Existing `last_delivered_id` still points at the same item id, but the **next** item in sequence may change relative to a pre-reorder manifest.
- [scripts/audit_post_images.py](scripts/audit_post_images.py): kanoninė ataskaita su fiksuotomis etiketėmis **A–I** (įrašų skaičius, unikalūs `image`, PNG skaičiai web/data, trūkumai, perteklius, kelių postų dalijimasis tuo pačiu PNG); aiškus skirtumas nuo planinio 1–100 slotų ataskaitos.
- [docs/POST_IMAGES.md](docs/POST_IMAGES.md): skiltis **Canonical metrics** — kodėl **A/D/C** nesutampa ir kaip skaičiuoti vienodai kiekvieną kartą.
- [web/public/images/posts/](web/public/images/posts/): `data/images` PNG kopijos sutapdintos su viešu katalogu (naršyklė / statinis deploy mato tuos pačius **74** basename kaip `data/images`).
- [`bot/handlers.py`](bot/handlers.py): `send_content_item` for shared send logic; [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/RUNBOOK.md`](docs/RUNBOOK.md), [`.env.example`](.env.example), [`docs/INDEX.md`](docs/INDEX.md).

### Removed

- **`scripts/merge_posts_text_from_generated.py`** (replaced by `sync_posts_json_from_generated_manifest.py`).

### Fixed

- **Railway deploy:** [`railway.toml`](railway.toml) previously set `builder = "NIXPACKS"`, which is **not** a valid Railway builder ([config-as-code](https://docs.railway.com/reference/config-as-code) allows **`RAILPACK`** or **`DOCKERFILE`** only). Switched to **`RAILPACK`**. Python pin in RUNBOOK: **`RAILPACK_PYTHON_VERSION`** (replaces obsolete `NIXPACKS_PYTHON_VERSION`).

- **Scheduled queue + state write:** after a successful Telegram send, if persisting `data/state.json` fails, the bot sends the same English warning to the admin DM as `/next` when `SCHEDULE_NOTIFY_ON_FAILURE` is enabled (default). Shared message text in [`bot/handlers.py`](bot/handlers.py). Tests in [`tests/test_handlers_scheduled.py`](tests/test_handlers_scheduled.py). [docs/RUNBOOK.md](docs/RUNBOOK.md) env table and troubleshooting row updated.
- **Docs / CI:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — PTB 21+ wording, clearer `state.json` / JSON error note, expanded contract-test file list, section **Long-lived core** (renamed from “Marry”). GitHub Actions **python** job runs pytest then `audit_posts_png_quizzes.py`; **api_ts** runs `check:api`; **web** job builds the app ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)); [docs/RUNBOOK.md](docs/RUNBOOK.md) (**API typecheck**, pre-push parity, local **python** job parity), [AGENTS.md](AGENTS.md) (Quality assurance for `api/` + audit), and [docs/INDEX.md](docs/INDEX.md) aligned.

## [0.3.10] - 2026-04-06

### Added

- [tests/test_orchestrator.py](tests/test_orchestrator.py): tests that `status_text()` next line matches `peek_next_item()`.

### Changed

- [orchestrator.py](orchestrator.py): `/status` via `status_text()` includes the next queue item `id` and `type` (aligned with `peek_next_item`).
- [bot/handlers.py](bot/handlers.py): `/start` help mentions `/status` shows the next item.
- [.env.example](.env.example): note that `/next` delivers to the command chat (`effective_chat`), not `ADMIN_CHAT_ID`.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): document `/status` next line and modules table tweak.
- [docs/INDEX.md](docs/INDEX.md): ARCHITECTURE index summary (`/status` next id/type) and Last reviewed.

## [0.3.9] - 2026-04-05

### Added

- [tsconfig.api.json](tsconfig.api.json), [package.json](package.json) script `check:api`, devDependency `typescript` ~5.9.3 — lokaliai: `npm run check:api`.

### Fixed

- [api/publish.ts](api/publish.ts): suderinamumas su **TypeScript 5.9** (`Blob` iš `ArrayBuffer` kopijos; `ok === false` susiaurinimas prieš `.detail` / `.phase`).

### Changed

- Vercel: publish API (`BOT_TOKEN` / `TELEGRAM_BOT_TOKEN`, `PUBLISH_CHAT_ID` / `TELEGRAM_PUBLISH_CHAT_ID`, `PUBLISH_BEARER_TOKEN`) turi būti **Project → Settings → Environment Variables** su pažymėta **Production** (ir **Preview**, jei naudoji preview URL); jei kintamieji tik prie vieno deployment ar tik Preview, production gali grąžinti 503 „Publish is not configured on the server.“

## [0.3.8] - 2026-04-04

### Fixed

- [api/publish.ts](api/publish.ts): nuotrauką serveris pats atsisiunčia iš to paties host ir siunčia Telegram kaip `multipart/form-data` (patikimesnė nei URL `sendPhoto`, kurią Telegram dažnai atmeta).
- [web/src/main.ts](web/src/main.ts): publikavimo klaidos pranešime rodomas API `detail` (Telegram / fetch paaiškinimas).
- [api/publish.ts](api/publish.ts), [web/src/main.ts](web/src/main.ts): maži paveikslėliai (≤~3MB) siunčiami **base64** iš naršyklės — apeina Vercel **Deployment Protection** 401 ant serverio `fetch`; didesniems — URL + optional `VERCEL_AUTOMATION_BYPASS_SECRET` (`x-vercel-protection-bypass`).

### Changed

- Patvirtinta produkcijoje (Vercel): web „Publikuoti į Telegram“ sėkmingai pristato **tekstą ir paveikslėlį**; sėkmės atveju UI rodo pranešimą „Įrašas išsiųstas į Telegram. Tekstas ir paveikslėlis.“ ([web/src/main.ts](web/src/main.ts)).

## [0.3.7] - 2026-04-03

### Added

- [api/publish.ts](api/publish.ts): optional JSON `photo` (HTTPS URL, same host as the request; `http://localhost` allowed for local dev) — `sendPhoto` with caption up to 1024 characters, remainder via `sendMessage` chunks; body may be photo-only.
- [web/src/main.ts](web/src/main.ts): „Publikuoti į Telegram“ sends `post.image` when set.

### Changed

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/RUNBOOK.md](docs/RUNBOOK.md), [docs/INDEX.md](docs/INDEX.md), [web/README.md](web/README.md): HTTP publish path dokumentuotas su optional nuotrauka ir same-host `photo` URL taisykle.

### Fixed

- [bot/main.py](bot/main.py): read `ADMIN_CHAT_ID` after `validate_config()` so `run_bot` sees the resolved id (avoids a stale `None` from import-time binding).

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
