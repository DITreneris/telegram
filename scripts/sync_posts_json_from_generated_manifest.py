"""Overwrite web/public/posts.json ``theme`` + ``content`` from data/content.generated.json.

Matches on ``related_post_id`` (same as social post ``id``). Rows whose ``id`` has no
``text`` item in the manifest are left unchanged (e.g. 62, 100 in some snapshots).

Optionally updates ``data/polls.json`` ``theme_note`` to the new headline per
``related_post_id`` so Telegram debrief lines stay aligned.

Usage (repo root)::

    python scripts/sync_posts_json_from_generated_manifest.py
    python scripts/sync_posts_json_from_generated_manifest.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_generated_map(generated_path: Path) -> dict[int, tuple[str, str]]:
    data = json.loads(generated_path.read_text(encoding="utf-8"))
    out: dict[int, tuple[str, str]] = {}
    for it in data.get("items", []):
        if it.get("type") != "text":
            continue
        pid = it.get("related_post_id")
        if not isinstance(pid, int):
            continue
        text = it.get("text")
        note = it.get("theme_note")
        if not isinstance(text, str) or not isinstance(note, str):
            continue
        out[pid] = (text, note.strip())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated", type=Path, default=Path("data/content.generated.json"))
    ap.add_argument("--posts", type=Path, default=Path("web/public/posts.json"))
    ap.add_argument("--polls", type=Path, default=Path("data/polls.json"))
    ap.add_argument("--no-polls", action="store_true", help="Do not update polls.json theme_note")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    gen_path = root / args.generated
    posts_path = root / args.posts
    polls_path = root / args.polls

    if not gen_path.is_file():
        raise SystemExit(f"Missing: {gen_path}")

    by_post = load_generated_map(gen_path)
    posts = json.loads(posts_path.read_text(encoding="utf-8"))

    updated: list[int] = []
    unchanged_missing: list[int] = []
    for row in posts:
        pid = int(row["id"])
        if pid not in by_post:
            unchanged_missing.append(pid)
            continue
        text, theme = by_post[pid]
        if row.get("theme") == theme and row.get("content") == text:
            continue
        row["theme"] = theme
        row["content"] = text
        row.pop("topic_key", None)
        updated.append(pid)

    print(f"Updated post ids ({len(updated)}): {sorted(updated)}")
    print(f"No manifest text - left as-is: {sorted(unchanged_missing)}")

    theme_by_id = {int(r["id"]): str(r["theme"]).strip() for r in posts}
    poll_updates = 0
    if not args.no_polls and polls_path.is_file():
        pdata = json.loads(polls_path.read_text(encoding="utf-8"))
        for item in pdata.get("items", []):
            rid = item.get("related_post_id")
            if not isinstance(rid, int):
                continue
            new_note = theme_by_id.get(rid)
            if not new_note:
                continue
            if item.get("theme_note") != new_note:
                item["theme_note"] = new_note
                poll_updates += 1
        print(f"Poll theme_note rows to write: {poll_updates}")

    if args.dry_run:
        return

    posts_path.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {posts_path}")
    if not args.no_polls and polls_path.is_file() and poll_updates:
        polls_path.write_text(json.dumps(pdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {polls_path}")


if __name__ == "__main__":
    main()
