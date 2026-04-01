"""Merge long-form bodies from post_longform_bodies_31_plus.py into web/public/posts.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from post_longform_bodies_31_plus import BODIES  # noqa: E402


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    posts_path = root / "web" / "public" / "posts.json"
    posts = json.loads(posts_path.read_text(encoding="utf-8"))
    updated = 0
    for row in posts:
        pid = row.get("id")
        if pid not in BODIES:
            continue
        row["content"] = BODIES[pid]
        updated += 1
    missing = set(BODIES.keys()) - {row["id"] for row in posts}
    if missing:
        raise SystemExit(f"No post rows for ids: {sorted(missing)}")
    posts_path.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {updated} posts in {posts_path}")


if __name__ == "__main__":
    main()
