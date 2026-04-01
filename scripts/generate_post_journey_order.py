"""Generate data/post_journey_order.json: curated interleaving of all post ids.

Uses bucket round-robin (fundamentals / role_stack / tool_map / other) so the
Telegram queue mixes card types without changing post ids.

Run from repo root:
  python scripts/generate_post_journey_order.py --dry-run
  python scripts/generate_post_journey_order.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from queue_manifest_sync import (  # noqa: E402
    POST_JOURNEY_ORDER_REL,
    load_posts_rows,
    order_posts_for_journey,
)

POSTS_PATH = ROOT / "web" / "public" / "posts.json"
OUT_PATH = ROOT / POST_JOURNEY_ORDER_REL

# Mirror scripts/realign_polls_with_posts.py ROLE_STACK_IDS (66 may be absent from posts.json).
ROLE_STACK_IDS: frozenset[int] = frozenset(
    {
        32,
        37,
        41,
        46,
        51,
        56,
        66,
        71,
        76,
        81,
        86,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
    }
)

TOOL_MAP_IDS: frozenset[int] = frozenset({31, 60, 62, 65, 70, 75, 100})


def build_ordered_ids(posts: list[dict]) -> list[int]:
    by_id = {int(r["id"]): r for r in posts}
    all_ids: set[int] = set(by_id)

    fund_posts = [by_id[i] for i in sorted(all_ids) if 1 <= i <= 30]
    fund_order = order_posts_for_journey(fund_posts)
    fundamentals: deque[int] = deque(int(r["id"]) for r in fund_order)

    role_stack: deque[int] = deque(sorted(i for i in all_ids if i in ROLE_STACK_IDS))
    tool_map: deque[int] = deque(sorted(i for i in all_ids if i in TOOL_MAP_IDS))

    claimed: set[int] = set(fundamentals) | set(role_stack) | set(tool_map)
    other: deque[int] = deque(sorted(all_ids - claimed))

    buckets: list[deque[int]] = [fundamentals, role_stack, tool_map, other]
    out: list[int] = []
    while any(buckets):
        for b in buckets:
            if b:
                out.append(b.popleft())

    if len(out) != len(all_ids) or set(out) != all_ids:
        raise RuntimeError("internal: round-robin did not cover all post ids")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Write data/post_journey_order.json")
    ap.add_argument("--dry-run", action="store_true", help="Print ids only, do not write")
    ap.add_argument("--limit", type=int, default=0, help="Print only first N ids with --dry-run")
    args = ap.parse_args()

    posts = load_posts_rows(POSTS_PATH)
    ids = build_ordered_ids(posts)

    if args.dry_run:
        lim = args.limit if args.limit > 0 else len(ids)
        print(f"post_ids ({len(ids)} total), first {min(lim, len(ids))}:")
        print(ids[:lim])
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps({"version": 1, "post_ids": ids}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH} ({len(ids)} ids)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
