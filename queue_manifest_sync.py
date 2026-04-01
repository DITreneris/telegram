"""Build data/content.json-style manifest from web/public/posts.json + data/polls.json."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from schemas import (
    MAX_CAPTION_CHARS,
    MAX_POLL_OPTION_CHARS,
    MAX_POLL_QUESTION_CHARS,
    MAX_POLL_OPTIONS,
    MIN_POLL_OPTIONS,
    parse_manifest,
)

# Photo path in repo for web asset convention `/images/posts/...` in posts.json.
WEB_PUBLIC_PREFIX = "web/public"

# Optional explicit queue order (same post ids, curated sequence). See docs/QUEUE_SYNC.md.
POST_JOURNEY_ORDER_REL = Path("data") / "post_journey_order.json"


def hook_caption(theme: str) -> str:
    """Telegram photo caption hook (matches MAX_CAPTION_CHARS)."""
    t = theme.strip()
    if len(t) <= MAX_CAPTION_CHARS:
        return t
    return t[: MAX_CAPTION_CHARS - 3].rstrip() + "..."


def image_to_relative_path(image: str) -> str:
    """Map `/images/posts/x.png` to `web/public/images/posts/x.png` (posix slashes)."""
    s = image.strip()
    if not s.startswith("/"):
        s = "/" + s
    return f"{WEB_PUBLIC_PREFIX}{s}".replace("\\", "/")


def load_posts_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"posts.json not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("posts.json must be a JSON array.")
    out: list[dict[str, Any]] = []
    for i, row in enumerate(raw):
        if not isinstance(row, dict):
            raise ValueError(f"posts.json[{i}] must be an object.")
        pid = row.get("id")
        if isinstance(pid, bool) or not isinstance(pid, int):
            raise ValueError(f"posts.json[{i}]: 'id' must be an integer.")
        theme = row.get("theme")
        if not isinstance(theme, str) or not theme.strip():
            raise ValueError(f"posts.json[{i}]: 'theme' must be a non-empty string.")
        content = row.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"posts.json[{i}]: 'content' must be a non-empty string.")
        tk_raw = row.get("topic_key")
        if tk_raw is not None:
            if not isinstance(tk_raw, str) or not tk_raw.strip():
                raise ValueError(
                    f'posts.json[{i}]: optional "topic_key" must be a non-empty string when set.'
                )
        out.append(row)
    return out


def effective_topic_key(row: dict[str, Any]) -> str:
    """Canonical topic for journey ordering: explicit topic_key or normalized theme."""
    tk = row.get("topic_key")
    if isinstance(tk, str):
        s = tk.strip()
        if s:
            return s
    return str(row["theme"]).strip().lower()


def order_posts_for_journey(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order posts so consecutive posts avoid repeating the same topic_key when possible.

    Greedy: pick from a topic different from the previous post; prefer the topic
    with the most remaining posts, then smallest front post id, then topic_key.
    """
    by_topic: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
    for row in sorted(posts, key=lambda r: int(r["id"])):
        by_topic[effective_topic_key(row)].append(row)

    result: list[dict[str, Any]] = []
    last_key: str | None = None

    def non_empty_keys() -> list[str]:
        return [k for k, q in by_topic.items() if q]

    while non_empty_keys():
        eligible = [k for k in non_empty_keys() if k != last_key]
        if eligible:
            chosen = sorted(
                eligible,
                key=lambda k: (-len(by_topic[k]), int(by_topic[k][0]["id"]), k),
            )[0]
        else:
            chosen = non_empty_keys()[0]
        row = by_topic[chosen].popleft()
        result.append(row)
        last_key = chosen
    return result


def journey_order_path(base_dir: Path) -> Path:
    return base_dir.resolve() / POST_JOURNEY_ORDER_REL


def load_post_journey_order(base_dir: Path) -> list[int] | None:
    """Load curated post id sequence from data/post_journey_order.json, or None if absent/unused."""
    path = journey_order_path(base_dir)
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1:
        return None
    ids = raw.get("post_ids")
    if not isinstance(ids, list) or not ids:
        return None
    out: list[int] = []
    for i, x in enumerate(ids):
        if isinstance(x, bool) or not isinstance(x, int):
            raise ValueError(f"post_journey_order.json post_ids[{i}] must be an integer.")
        out.append(x)
    return out


def validate_journey_order_ids(*, post_ids: list[int], valid_ids: set[int]) -> None:
    """Require exact permutation of all posts.json ids (strict)."""
    n = len(valid_ids)
    if len(post_ids) != n:
        raise ValueError(
            f"post_journey_order.json: expected {n} post_ids, got {len(post_ids)}."
        )
    if len(set(post_ids)) != len(post_ids):
        raise ValueError("post_journey_order.json: duplicate post_ids.")
    missing = valid_ids - set(post_ids)
    extra = set(post_ids) - valid_ids
    if missing or extra:
        raise ValueError(
            f"post_journey_order.json: id set mismatch (missing={sorted(missing)}, extra={sorted(extra)})."
        )


def apply_explicit_post_order(
    posts: list[dict[str, Any]], ordered_ids: list[int]
) -> list[dict[str, Any]]:
    by_id = {int(r["id"]): r for r in posts}
    return [by_id[pid] for pid in ordered_ids]


def resolve_post_order(posts: list[dict[str, Any]], base_dir: Path) -> list[dict[str, Any]]:
    """Use data/post_journey_order.json when valid; otherwise order_posts_for_journey."""
    ordered = load_post_journey_order(base_dir)
    if ordered is None:
        return order_posts_for_journey(posts)
    valid_ids = {int(p["id"]) for p in posts}
    validate_journey_order_ids(post_ids=ordered, valid_ids=valid_ids)
    return apply_explicit_post_order(posts, ordered)


def load_poll_bank(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"polls bank not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("polls.json root must be an object.")
    if raw.get("version") != 1:
        raise ValueError('polls.json "version" must be 1.')
    items = raw.get("items")
    if not isinstance(items, list):
        raise ValueError('polls.json "items" must be an array.')
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for i, row in enumerate(items):
        if not isinstance(row, dict):
            raise ValueError(f"polls.json items[{i}] must be an object.")
        qid = row.get("id")
        if not isinstance(qid, str) or not qid.strip():
            raise ValueError(f"polls.json items[{i}]: 'id' must be a non-empty string.")
        if qid in seen:
            raise ValueError(f"polls.json duplicate poll id: {qid!r}")
        seen.add(qid)
        rid = row.get("related_post_id")
        if isinstance(rid, bool) or not isinstance(rid, int) or rid < 1:
            raise ValueError(f"polls.json items[{i}]: 'related_post_id' must be int >= 1.")
        question = row.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"polls.json items[{i}]: 'question' must be a non-empty string.")
        if len(question) > MAX_POLL_QUESTION_CHARS:
            raise ValueError(
                f"polls.json items[{i}]: 'question' exceeds {MAX_POLL_QUESTION_CHARS} chars."
            )
        opts = row.get("options")
        if not isinstance(opts, list) or not MIN_POLL_OPTIONS <= len(opts) <= MAX_POLL_OPTIONS:
            raise ValueError(
                f"polls.json items[{i}]: 'options' must have {MIN_POLL_OPTIONS}–{MAX_POLL_OPTIONS} entries."
            )
        for j, o in enumerate(opts):
            if not isinstance(o, str) or not o.strip():
                raise ValueError(f"polls.json items[{i}] options[{j}] must be a non-empty string.")
            if len(o) > MAX_POLL_OPTION_CHARS:
                raise ValueError(
                    f"polls.json items[{i}] options[{j}] exceeds {MAX_POLL_OPTION_CHARS} chars."
                )
        cid = row.get("correct_option_id")
        if isinstance(cid, bool) or not isinstance(cid, int):
            raise ValueError(
                f"polls.json items[{i}]: 'correct_option_id' must be an integer (0 … n-1)."
            )
        if not 0 <= cid < len(opts):
            raise ValueError(f"polls.json items[{i}]: 'correct_option_id' out of range.")
        theme_note = row.get("theme_note")
        if theme_note is not None and (not isinstance(theme_note, str) or not theme_note.strip()):
            raise ValueError(f"polls.json items[{i}]: 'theme_note' must be non-empty string or absent.")
        out.append(row)
    return out


def validate_poll_post_ids(polls: list[dict[str, Any]], post_ids: set[int]) -> None:
    for row in polls:
        rid = row["related_post_id"]
        if rid not in post_ids:
            raise ValueError(
                f"poll id {row['id']!r}: related_post_id {rid} not found in posts.json ids."
            )


def poll_row_to_manifest_item(row: dict[str, Any]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": row["id"],
        "type": "poll",
        "question": row["question"].strip(),
        "options": [str(o).strip() for o in row["options"]],
        "correct_option_id": row["correct_option_id"],
        "related_post_id": row["related_post_id"],
    }
    tn = row.get("theme_note")
    if isinstance(tn, str) and tn.strip():
        item["theme_note"] = tn.strip()
    return item


def build_manifest_dict(*, base_dir: Path, posts: list[dict[str, Any]], polls: list[dict[str, Any]]) -> dict[str, Any]:
    """Assemble ordered items: per-post photo (if file exists) + text + linked quizzes."""
    root = base_dir.resolve()
    posts_sorted = resolve_post_order(posts, root)
    post_ids = {int(p["id"]) for p in posts_sorted}
    validate_poll_post_ids(polls, post_ids)

    polls_by_post: dict[int, list[dict[str, Any]]] = {pid: [] for pid in post_ids}
    for p in polls:
        polls_by_post[int(p["related_post_id"])].append(p)
    for pid in polls_by_post:
        polls_by_post[pid].sort(key=lambda x: str(x["id"]))

    items_out: list[dict[str, Any]] = []

    for row in posts_sorted:
        pid = int(row["id"])
        theme = str(row["theme"]).strip()
        content = str(row["content"]).strip()
        image = row.get("image")
        rel_photo: str | None = None
        if isinstance(image, str) and image.strip():
            rel_photo = image_to_relative_path(image)
            if not (root / rel_photo).is_file():
                rel_photo = None

        if rel_photo:
            items_out.append(
                {
                    "id": f"post_{pid:03d}_photo",
                    "type": "photo",
                    "path": rel_photo,
                    "caption": hook_caption(theme),
                    "related_post_id": pid,
                    "theme_note": theme,
                }
            )
        items_out.append(
            {
                "id": f"post_{pid:03d}_text",
                "type": "text",
                "text": content,
                "related_post_id": pid,
                "theme_note": theme,
            }
        )
        for poll_row in polls_by_post[pid]:
            items_out.append(poll_row_to_manifest_item(poll_row))

    return {"version": 1, "items": items_out}


def build_and_validate_manifest(
    *, base_dir: Path, posts_path: Path, polls_path: Path
) -> dict[str, Any]:
    """Load sources, build manifest dict, run parse_manifest for full validation."""
    posts = load_posts_rows(posts_path)
    polls = load_poll_bank(polls_path)
    raw = build_manifest_dict(base_dir=base_dir, posts=posts, polls=polls)
    parse_manifest(raw, base_dir=base_dir)
    return raw


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
