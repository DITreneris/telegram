# Documentation index

Master list of project documentation. **Update this file** whenever you add, rename, or remove a doc under `docs/`.

For **how** the index, changelog, and reviews fit together, see [VERSIONING.md](VERSIONING.md). Release history: [CHANGELOG.md](../CHANGELOG.md).

| Path | Audience | Summary | Last reviewed |
|------|----------|---------|---------------|
| [INDEX.md](INDEX.md) | Human, agent | This index; links to changelog and versioning policy | 2026-03-31 |
| [VERSIONING.md](VERSIONING.md) | Human, agent | Documentation management: index, archive folder, changelog (Unreleased vs version section), Last reviewed, semver notes | 2026-03-29 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Human, agent | Modules, data flow, **production shape** (Railway bot + Vercel web), queue bot + JobQueue + HTTP publish, KISS + Marry, manifest/state, `/status` next id/type, env schedule flags | 2026-04-01 |
| [RUNBOOK.md](RUNBOOK.md) | Human, agent | Setup, env vars, **Railway** queue-bot hosting (`state.json` caveat, one replica), run, tests + **API typecheck**, CI, **Quick operator rules**, Vercel web/publish vs bot, troubleshooting, EN Telegram bot messages; poll `theme_note` debrief | 2026-04-01 |
| [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md) | Human, agent | `posts.json` authoring; quiz ↔ lesson alignment; **batch QA checklist** (audits → sync → pytest); **`audit_post_quiz_semantics.py`**; **`restore_posts_png_aligned.py`**; optional manifest sync / `merge_longform_posts.py` | 2026-03-31 |
| [QUEUE_SYNC.md](QUEUE_SYNC.md) | Human, agent | Build `data/content.json` from `posts.json` + `data/polls.json` (photo + text + quiz polls); poll `theme_note` → follow-up message after quiz; optional `topic_key` / greedy journey order **or** `data/post_journey_order.json`; sync CLI | 2026-03-31 |
| [POST_IMAGES.md](POST_IMAGES.md) | Human, agent | PNG coverage vs `posts.json`: metrics A–I; run `audit_post_images.py` and/or `audit_posts_png_quizzes.py`; align rows with `merge_posts_json_from_png.py` | 2026-03-31 |
| [CONTENT_INVENTORY.md](CONTENT_INVENTORY.md) | Human, agent | Single snapshot: posts + web/data PNG + `polls.json`; regenerate via `audit_posts_png_quizzes.py --write-inventory`; also `merge_posts_json_from_png.py`, `fill_stub_posts_and_expand_polls.py` | 2026-03-31 |
| [MISSING_POST_IMAGES.md](MISSING_POST_IMAGES.md) | Human, agent | Lentelė trūkstamiems PNG (`id`, tema); generuoja `scripts/gen_missing_post_images_md.py` | 2026-03-31 |
| [POST_IMAGES_GAP_1_100.md](POST_IMAGES_GAP_1_100.md) | Human, agent | **Plano** slotai 1–100 (ne tas pats kas dabartinis `posts.json` eilučių skaičius) vs diskas; `scripts/gen_post_images_gap_report.py` | 2026-03-31 |

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
| [../CHANGELOG.md](../CHANGELOG.md) | Notable changes (code + material docs); Keep a Changelog style |
| [../.env.example](../.env.example) | Environment variable template and local run steps |
| [../railway.toml](../railway.toml) | Railway worker: **RAILPACK** + `python run.py` (queue bot); see RUNBOOK |
| [../web/public/posts.json](../web/public/posts.json) | Social post rows (`id`, `theme`, `content`, `image` path) — canonical for copy + PNG reference |
| [../data/polls.json](../data/polls.json) | Quiz bank; `related_post_id` ties each poll to a post |
| [../web/public/polls.json](../web/public/polls.json) | Web/Vite copy of quiz bank (build sync; often gitignored) |
| [../data/content.json](../data/content.json) | Live Telegram queue manifest (regenerate: `python scripts/sync_queue_from_posts.py --in-place`) |
| [../data/post_journey_order.json](../data/post_journey_order.json) | Optional curated post `id` order for the queue; `generate_post_journey_order.py` writes it; [QUEUE_SYNC.md](QUEUE_SYNC.md#explicit-journey-order) |
| [../queue_manifest_sync.py](../queue_manifest_sync.py) | Merge `posts.json` + `polls.json` into manifest items (photo, text, poll, ordering) |
| [../scripts/sync_queue_from_posts.py](../scripts/sync_queue_from_posts.py) | CLI for that merge; default out `data/content.generated.json`, `--in-place` → `data/content.json` |
| [../scripts/generate_post_journey_order.py](../scripts/generate_post_journey_order.py) | Generate `data/post_journey_order.json` (bucketed round-robin) |
| [../scripts/audit_posts_png_quizzes.py](../scripts/audit_posts_png_quizzes.py) | Audit posts ↔ PNG ↔ polls (run before trusting counts) |
