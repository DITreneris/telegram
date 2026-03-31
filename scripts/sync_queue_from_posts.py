#!/usr/bin/env python3
"""Merge web/public/posts.json + data/polls.json into a content manifest (content.json shape)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from queue_manifest_sync import (  # noqa: E402
    build_and_validate_manifest,
    write_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build queue manifest from posts.json + data/polls.json (validates via schemas)."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=_REPO_ROOT,
        help="Repository root (default: repo containing this script).",
    )
    parser.add_argument(
        "--posts",
        type=Path,
        default=None,
        help="Path to posts.json (default: <base-dir>/web/public/posts.json).",
    )
    parser.add_argument(
        "--polls",
        type=Path,
        default=None,
        help="Path to polls bank (default: <base-dir>/data/polls.json).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output manifest (default: <base-dir>/data/content.generated.json).",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write <base-dir>/data/content.json instead of content.generated.json.",
    )
    args = parser.parse_args()
    base_dir = args.base_dir.resolve()
    posts_path = args.posts or (base_dir / "web" / "public" / "posts.json")
    polls_path = args.polls or (base_dir / "data" / "polls.json")
    if args.in_place:
        out_path = base_dir / "data" / "content.json"
    else:
        out_path = args.out or (base_dir / "data" / "content.generated.json")

    try:
        manifest = build_and_validate_manifest(
            base_dir=base_dir,
            posts_path=posts_path,
            polls_path=polls_path,
        )
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    write_manifest(out_path, manifest)
    print(f"Wrote {out_path} ({len(manifest['items'])} items).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
