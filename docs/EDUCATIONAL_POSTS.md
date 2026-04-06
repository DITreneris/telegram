# Educational posts — “golden standard” authoring

Use this doc when you want **longer, non-stub** copy than the short blocks in [`web/public/posts.json`](../web/public/posts.json). Quizzes in [`data/polls.json`](../data/polls.json) should **test the specific lesson** of that slot, not a generic “structured vs vague” template.

## When to edit by hand

- **Posts 1–30:** Full narrative bodies already live in `posts.json` (three rotations over the same core themes). Refine tone and examples there; align each quiz to the **angle of that wave** (mirror inputs, politeness vs precision, guessing vs design, etc.).
- **Posts 31+ — PNG slot = headline:** Canonical **`theme` per `NN_Prompt_Anatomy.png`** lives in [`scripts/fill_stub_posts_and_expand_polls.py`](../scripts/fill_stub_posts_and_expand_polls.py) (`SLOT_THEMES`) and [`scripts/gen_post_images_gap_report.py`](../scripts/gen_post_images_gap_report.py) (`PLANNED_THEME_BY_SLOT`, e.g. slot **31**). To reset **`theme` + stub `content` + polls + queue** to that map (when copy drifted from another manifest), run [`scripts/restore_posts_png_aligned.py`](../scripts/restore_posts_png_aligned.py). Optional longer bodies: [`scripts/post_longform_bodies_31_plus.py`](../scripts/post_longform_bodies_31_plus.py) + [`scripts/merge_longform_posts.py`](../scripts/merge_longform_posts.py). Experimental sync from a local `content.generated.json`: [`scripts/sync_posts_json_from_generated_manifest.py`](../scripts/sync_posts_json_from_generated_manifest.py) + [`scripts/realign_polls_with_posts.py`](../scripts/realign_polls_with_posts.py). After edits: [`QUEUE_SYNC.md`](QUEUE_SYNC.md).

## Golden-standard post skeleton

1. **Hook** — One line tension (matches PNG / social headline).
2. **Problem** — What the reader does wrong (vague ask, wrong lever, tool fixation).
3. **Reframe** — The mental model (system, brief, compliance, rubric).
4. **Concrete pattern** — Bullets or before/after prompt snippets (English).
5. **Constraint** — Length, audience, or format the reader can copy.
6. **CTA** — Single next step (e.g. link to promptanatomy.app).

Keep Telegram-facing bot copy **English** per project rules.

## PNG vs body (asset backlog)

Some slots (e.g. **9, 19, 29**) may keep a **confrontational or percentage-style hook on the PNG** while **body** copy follows epistemic hygiene (no fake census stats). **Aligning image and body** requires new or revised artwork—not only `posts.json`. Track as a design backlog item when refreshing the deck.

**Role-stack cards** (“How [role] uses AI: decisions & stack”): you may vary **hooks, bridges, and closings** to reduce repetitive rhythm as long as **layer meanings, tool names, and URLs** in each `🔹` block stay the same and the lesson remains *decisions + layered workflow*.

## Quiz design rules

- **One lesson per post:** The question should fail if the reader only memorized “pick the longer option.”
- **Plausible wrong option:** Same topic, wrong lever (e.g. “switch models” vs “tighten constraints”).
- **Binary default:** The bot manifest and UX assume **two options** today. **Three-option** (near-miss distractors) is allowed by [schemas.py](../schemas.py) and Telegram, but needs a deliberate product pass (copy + any handler copy). See also [CURRICULUM_UX_AUDIT.md](CURRICULUM_UX_AUDIT.md) §4.
- **`theme_note`:** Short debrief after the quiz—tie back to the post headline when possible.
- **Batch tooling:** [`scripts/fill_stub_posts_and_expand_polls.py`](../scripts/fill_stub_posts_and_expand_polls.py) fills coverage; [`scripts/apply_poll_lesson_patches.py`](../scripts/apply_poll_lesson_patches.py) can refresh lesson quizzes when themes stay on the “prompt craft” track.
- **Heuristic QA:** [`scripts/audit_post_quiz_semantics.py`](../scripts/audit_post_quiz_semantics.py) — lists generic stub bodies, `theme_note` vs `theme` mismatches, and low token overlap between poll `question` and post text (rough signal only).

## Batch QA checklist (after a large `posts.json` / `polls.json` edit)

From repo root, in order:

1. **Structure:** `python scripts/audit_posts_png_quizzes.py` — posts ↔ PNG ↔ polls coverage and id/slot integrity (optional: `--write-inventory docs/CONTENT_INVENTORY.md`).
2. **Semantics (heuristic):** `python scripts/audit_post_quiz_semantics.py` — fix any generic stub bodies; align `theme_note` with post `theme` when it differs; treat “low question overlap” as a manual review list (not auto-fix).
3. **Queue + tests:** `python scripts/sync_queue_from_posts.py --in-place`; if you changed `theme`, also sync `theme_note` in [`data/polls.json`](../data/polls.json), run `node scripts/sync_polls_to_web.mjs` when using the web app, then `pytest`.

## Restore `posts.json` from `content.generated.json`

If stacks / tool lists exist only under **`data/content.generated.json`**, run from repo root:

1. `python scripts/sync_posts_json_from_generated_manifest.py` — copies **`theme` + `content`** by `related_post_id` into [`web/public/posts.json`](../web/public/posts.json); updates **`data/polls.json`** `theme_note` to match headlines; use `--dry-run` first if unsure. Rows with no manifest text (e.g. **62**, **100**) are left unchanged.
2. `python scripts/realign_polls_with_posts.py` — refreshes quiz **questions** for the role-stack and tailored ids after a sync.

## Related docs

- [`QUEUE_SYNC.md`](QUEUE_SYNC.md) — manifest merge from `posts.json` + `polls.json`; optional bot deck order via [`data/post_journey_order.json`](../data/post_journey_order.json) ([Explicit journey order](QUEUE_SYNC.md#explicit-journey-order))
- [`CONTENT_INVENTORY.md`](CONTENT_INVENTORY.md) — PNG vs post vs quiz coverage
- [`POST_IMAGES.md`](POST_IMAGES.md) — deck and audit scripts
