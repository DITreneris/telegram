# Documentation index

Master list of project documentation. **Update this file** whenever you add, rename, or remove a doc under `docs/`.

For **how** the index, changelog, and reviews fit together, see [VERSIONING.md](VERSIONING.md). Release history: [CHANGELOG.md](../CHANGELOG.md).

| Path | Audience | Summary | Last reviewed |
|------|----------|---------|---------------|
| [INDEX.md](INDEX.md) | Human, agent | This index; links to changelog and versioning policy | 2026-04-05 |
| [VERSIONING.md](VERSIONING.md) | Human, agent | Documentation management: index, archive folder, changelog (Unreleased vs version section), Last reviewed, semver notes | 2026-03-29 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Human, agent | Modules, data flow, **production shape** (Railway bot + Vercel web), queue bot + JobQueue + HTTP publish, KISS + Marry, manifest/state, `/status` next id/type, **`post_init` / scoped command menu**, inline Next/Status, `bot/bot_copy.py`, env schedule flags (six daily slots 08:00/08:15/08:30 + 19:00/19:15/19:30 `SCHEDULE_TZ`), **error_handler**, long-text chunking (`MAX_MESSAGE_CHARS`), `_next_lock` | 2026-04-05 |
| [RUNBOOK.md](RUNBOOK.md) | Human, agent | Setup, env vars, **`QUEUE_STATE_PATH`** + Railway **volume** for persistent queue cursor, **pre-production deployment checklist**, **when bot is running** (smoke check, `/start` inline Next/Status, admin-scoped command menu, **BotFather** paste source [bot/bot_copy.py](../bot/bot_copy.py)), **Railway** queue-bot hosting (one replica), run, tests + **API typecheck** + **`npm run test:api`**, CI (**dependency_audit** / **pip_audit** advisory), **Quick operator rules**, **Publish API security**, Vercel web/publish vs bot, troubleshooting, EN Telegram bot messages; poll `theme_note` debrief; scheduled posting six daily times | 2026-04-05 |
| [golden_standard.md](golden_standard.md) | Human, agent | **Regression barrier:** CI commands (mirror Actions), architectural invariants, test map, content pipeline (incl. web **polls sync** before build, optional quiz semantics / rotate scripts); keep §1 in sync with [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | 2026-04-05 |
| [ROADMAP.md](ROADMAP.md) | Human, agent | Datuoti planuojami etapai (ne sutartis); bazinė data ir ketvirčio peržiūros; nuorodos į RUNBOOK, golden_standard, pipeline | 2026-04-04 |
| [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md) | Human, agent | `posts.json` authoring; quiz ↔ lesson alignment; **binary vs 3-option polls** (product note); **PNG vs body** asset backlog (e.g. 9/19/29 hooks); **batch QA checklist** (audits → sync → pytest); **`audit_post_quiz_semantics.py`**; **`restore_posts_png_aligned.py`**; optional manifest sync / `merge_longform_posts.py` | 2026-04-05 |
| [QUEUE_SYNC.md](QUEUE_SYNC.md) | Human, agent | Build `data/content.json` from `posts.json` + `data/polls.json` (photo + text + quiz polls); poll `theme_note` → follow-up message after quiz; optional `topic_key` / greedy journey order **or** `data/post_journey_order.json`; sync CLI | 2026-03-31 |
| [POST_IMAGES.md](POST_IMAGES.md) | Human, agent | PNG coverage vs `posts.json`: metrics A–I; run `audit_post_images.py` and/or `audit_posts_png_quizzes.py`; align rows with `merge_posts_json_from_png.py` | 2026-03-31 |
| [CONTENT_INVENTORY.md](CONTENT_INVENTORY.md) | Human, agent | Single snapshot: posts + web/data PNG + `polls.json`; regenerate via `audit_posts_png_quizzes.py --write-inventory`; also `merge_posts_json_from_png.py`, `fill_stub_posts_and_expand_polls.py` | 2026-03-31 |
| [MISSING_POST_IMAGES.md](MISSING_POST_IMAGES.md) | Human, agent | Lentelė trūkstamiems PNG (`id`, tema); generuoja `scripts/gen_missing_post_images_md.py` | 2026-03-31 |
| [POST_IMAGES_GAP_1_100.md](POST_IMAGES_GAP_1_100.md) | Human, agent | **Plano** slotai 1–100 (ne tas pats kas dabartinis `posts.json` eilučių skaičius) vs diskas; `scripts/gen_post_images_gap_report.py` | 2026-03-31 |
| [CURRICULUM_UX_AUDIT.md](CURRICULUM_UX_AUDIT.md) | Human, agent | Learner UX + pedagogy + SEL audit of `posts.json` / `polls.json`: rubric, redundancy (core ×3, role stacks, layer framework), quiz position bias, weakest posts + improvements; links **full run** [CURRICULUM_UX_AUDIT_FULL_2026-04-05.md](CURRICULUM_UX_AUDIT_FULL_2026-04-05.md) | 2026-04-05 |
| [UX_CONVERSION_AUDIT_PROMPT.md](UX_CONVERSION_AUDIT_PROMPT.md) | Human, agent | Copy-paste **LLM META** for long-form UX + conversion audit: repo-scoped input/output, **KISS–Marry–Kill** triage, **low hanging fruits** table, extended TOP 10 weakest units, before/after copy | 2026-04-05 |
| [CURRICULUM_UX_AUDIT_FULL_2026-04-05.md](CURRICULUM_UX_AUDIT_FULL_2026-04-05.md) | Human, agent | **Full 98-post** UX + conversion audit run: executive summary, journey, TOP 10, LHF table, KMK, quick wins, deep fixes, before/after; appendix wave map + metrics | 2026-04-05 |

## Archive (non-canonical)

Historical or exploratory material; **not** the live spec. See [archive/README.md](archive/README.md).

| Path | Summary |
|------|---------|
| [archive/README.md](archive/README.md) | What belongs in `docs/archive/` and how it relates to the canonical index |
| [archive/bot_concept_notes.txt](archive/bot_concept_notes.txt) | Alternate architecture notes (e.g. cycle_length); canonical: [ARCHITECTURE.md](ARCHITECTURE.md) + `content.json` v1 |
| [archive/30_posts.txt](archive/30_posts.txt) | Legacy social posts JSON (old root filename); canonical UI data: [web/public/posts.json](../web/public/posts.json) |

**Compatibility:** [bot_concept_notes.txt](bot_concept_notes.txt) is a short pointer at the former path so old links still work.

## `.txt` files in this repo (what they are)

| Location | Role |
|----------|------|
| [../requirements.txt](../requirements.txt), [../requirements-dev.txt](../requirements-dev.txt) | **pip** dependency lists (not prose docs). Keep as `.txt` by convention. |
| [bot_concept_notes.txt](bot_concept_notes.txt) | Short redirect only; full notes in [archive/bot_concept_notes.txt](archive/bot_concept_notes.txt). |
| [archive/*.txt](archive/) | Archived snapshots / notes (see [archive/README.md](archive/README.md)). |

## Related repo files (not under `docs/`)

| Path | Summary |
|------|---------|
| [../AGENTS.md](../AGENTS.md) | Entry point: purpose, **Content pipeline** (posts → polls → `content.json`), module map, Cursor rules/skills |
| [../bot/bot_copy.py](../bot/bot_copy.py) | Canonical EN strings: `/start`, BotFather Description/About (manual paste), `set_my_commands` labels |
| [../CHANGELOG.md](../CHANGELOG.md) | Notable changes (code + material docs); Keep a Changelog style |
| [../.env.example](../.env.example) | Environment variable template and local run steps |
| [../railway.toml](../railway.toml) | Railway config-as-code: **RAILPACK** builder, `startCommand = python run.py` (queue bot, one replica); see RUNBOOK |
| [../.github/workflows/ci.yml](../.github/workflows/ci.yml) | CI: pytest + audit, api_ts typecheck + `test:api`, web build, advisory npm/pip audit jobs — see RUNBOOK, golden_standard |
| [../web/public/posts.json](../web/public/posts.json) | Social post rows (`id`, `theme`, `content`, `image` path) — canonical for copy + PNG reference |
| [../data/polls.json](../data/polls.json) | Quiz bank; `related_post_id` ties each poll to a post |
| [../web/public/polls.json](../web/public/polls.json) | Web/Vite copy of quiz bank (build sync; often gitignored) |
| [../data/content.json](../data/content.json) | Live Telegram queue manifest (regenerate: `python scripts/sync_queue_from_posts.py --in-place`) |
| [../data/post_journey_order.json](../data/post_journey_order.json) | Optional curated post `id` order for the queue; `generate_post_journey_order.py` writes it; [QUEUE_SYNC.md](QUEUE_SYNC.md#explicit-journey-order) |
| [../queue_manifest_sync.py](../queue_manifest_sync.py) | Merge `posts.json` + `polls.json` into manifest items (photo, text, poll, ordering) |
| [../scripts/sync_queue_from_posts.py](../scripts/sync_queue_from_posts.py) | CLI for that merge; default out `data/content.generated.json`, `--in-place` → `data/content.json` |
| [../scripts/generate_post_journey_order.py](../scripts/generate_post_journey_order.py) | Generate `data/post_journey_order.json` (bucketed round-robin) |
| [../scripts/audit_posts_png_quizzes.py](../scripts/audit_posts_png_quizzes.py) | Audit posts ↔ PNG ↔ polls (run before trusting counts) |
| [../scripts/audit_post_quiz_semantics.py](../scripts/audit_post_quiz_semantics.py) | Optional heuristic: post body ↔ quiz question overlap (not CI) |
| [../scripts/rotate_poll_correct_options.py](../scripts/rotate_poll_correct_options.py) | Optional bulk alternation of binary `correct_option_id` |
