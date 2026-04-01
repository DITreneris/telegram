# Queue manifest from posts + quizzes

Canonical social copy lives in [web/public/posts.json](../web/public/posts.json) (see [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md)). The Telegram queue bot reads [data/content.json](../data/content.json). This doc describes how to **generate** a manifest that ties both together and inserts **Telegram quiz polls** aligned to post `id` / `theme`.

## Files

| File | Role |
|------|------|
| [web/public/posts.json](../web/public/posts.json) | Source rows: `id`, `theme`, `content`, optional `image`, optional `topic_key` |
| [data/polls.json](../data/polls.json) | Quiz bank: `version` `1`, `items[]` with `id`, `related_post_id`, `question`, `options`, `correct_option_id`, optional `theme_note` |
| [data/post_journey_order.json](../data/post_journey_order.json) | **Optional.** Curated Telegram delivery order: `version` `1`, `post_ids` — full permutation of every post `id` (see [Explicit journey order](#explicit-journey-order)) |
| [queue_manifest_sync.py](../queue_manifest_sync.py) | Pure merge + validation (calls `schemas.parse_manifest`) |
| [scripts/sync_queue_from_posts.py](../scripts/sync_queue_from_posts.py) | CLI wrapper |
| [scripts/generate_post_journey_order.py](../scripts/generate_post_journey_order.py) | Writes `data/post_journey_order.json` (bucketed round-robin starter order) |

## Rules

- **English** for all `question` and `options` text (what members see in Telegram).
- **KISS / Marry / Kill** when authoring quizzes: one clear teaching moment; correct option encodes the durable principle (**Marry**); wrong options embody the habit you retire (**Kill**). See [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md#kiss-marry-kill-quality-rubric--not-post-headings).
- **Telegram limits** (enforced by validation): question ≤ 300 characters; each option ≤ 100 characters; 2–10 options; `correct_option_id` is 0-based. For **`poll`** items, optional `theme_note` is also capped at **4096** characters ([`schemas.MAX_MESSAGE_CHARS`](../schemas.py)) because the bot may send it as a follow-up message after the quiz.
- Every `related_post_id` in `polls.json` must exist as an `id` in `posts.json`.
- **`topic_key`** (optional): short stable slug grouping variants of the same idea (e.g. multiple `option` rows sharing one curriculum theme). If omitted, merge uses a normalized `theme` string (`strip` + lowercase) for ordering only.
- **Order** in the generated manifest: if [`data/post_journey_order.json`](../data/post_journey_order.json) is present and valid, posts follow that `post_ids` list; otherwise [`order_posts_for_journey`](../queue_manifest_sync.py) (greedy interleaving by `topic_key` / normalized `theme`). Within each post: optional **photo** (only if `web/public/...` file exists) with caption = `theme` trimmed to [schemas.MAX_CAPTION_CHARS](../schemas.py); then **full text** body; then all quizzes for that `related_post_id` (sorted by quiz `id`). Photo then text for the same post stay back-to-back.

## CLI

From repo root (Python env with project imports available):

Optional: fill missing `topic_key` from known `theme` strings (and slug fallback for others):

```bash
python scripts/backfill_post_topic_keys.py
```

```bash
python scripts/sync_queue_from_posts.py
```

Default output: `data/content.generated.json` (gitignored). Replace the live queue when ready:

```bash
python scripts/sync_queue_from_posts.py --in-place
```

Options: `--base-dir`, `--posts`, `--polls`, `--out` (see `--help`).

## Explicit journey order

Commit [`data/post_journey_order.json`](../data/post_journey_order.json) when you want a **fixed** full-deck order for the Telegram queue (same post `id`s as `posts.json`, different sequence than the default greedy journey).

- **Shape:** `{"version": 1, "post_ids": [<int>, ...]}`. Must include **every** post `id` exactly once (no duplicates, no extras); otherwise merge raises `ValueError`. If the file is missing or `version` is not `1`, merge falls back to `order_posts_for_journey`.
- **Regenerate a starter file** (bucketed round-robin from `posts.json`; fundamentals 1–30 keep internal journey order):

  ```bash
  python scripts/generate_post_journey_order.py
  ```

  Use `--dry-run` to print the first N ids without writing.
- **After editing** the journey file or `posts.json`, refresh the live manifest:

  ```bash
  python scripts/sync_queue_from_posts.py --in-place
  ```

The **web** UI may still sort or list posts by `id` or theme — that display order is independent of the bot queue until the UI is extended to read journey order.

## Manifest fields

Besides `text` | `photo` | `document`, items may be **`poll`** (Telegram quiz):

- `question`, `options`, `correct_option_id`
- Optional on any item type: `related_post_id`, `theme_note`
- For **`poll`** items: if `theme_note` is present, the queue bot sends it as a **separate chat message immediately after** `send_poll` (short debrief / takeaway). Other item types keep `theme_note` as author metadata only unless extended later.

Full validation: [schemas.parse_manifest](../schemas.py).

## Tests

[`tests/test_queue_manifest_sync.py`](../tests/test_queue_manifest_sync.py), [`tests/test_schemas.py`](../tests/test_schemas.py) (poll rows), handler tests for `send_poll`.
