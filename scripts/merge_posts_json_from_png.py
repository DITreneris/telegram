"""Build web/public/posts.json: one row per NN_Prompt_Anatomy.png on disk.

Preserves theme/content/option/topic_key when post id matches slot number.
Forces canonical image path. Drops post rows whose id has no matching PNG.

Run from repo root:
  python scripts/merge_posts_json_from_png.py --dry-run
  python scripts/merge_posts_json_from_png.py --write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from gen_post_images_gap_report import PLANNED_THEME_BY_SLOT  # noqa: E402

POSTS_PATH = ROOT / "web" / "public" / "posts.json"
IMG_WEB = ROOT / "web" / "public" / "images" / "posts"

PNG_NAME_RE = re.compile(r"^(\d+)_Prompt_Anatomy\.png$")


def slot_from_basename(name: str) -> int | None:
    m = PNG_NAME_RE.match(name)
    return int(m.group(1)) if m else None


def png_slots_web() -> dict[int, str]:
    """slot -> basename for each Prompt Anatomy PNG in web public folder."""
    if not IMG_WEB.is_dir():
        return {}
    out: dict[int, str] = {}
    for p in IMG_WEB.glob("*.png"):
        slot = slot_from_basename(p.name)
        if slot is None:
            continue
        out[slot] = p.name
    return out


def stub_content(slot: int, theme: str) -> str:
    return (
        f"TODO: Replace with full post body for this card (slot {slot}).\n\n"
        f"Theme: {theme}\n\n"
        "→ https://promptanatomy.app\n"
    )


def build_merged_rows(
    existing_by_id: dict[int, dict],
    slot_to_basename: dict[int, str],
) -> list[dict]:
    rows: list[dict] = []
    for slot in sorted(slot_to_basename.keys()):
        basename = slot_to_basename[slot]
        image_path = f"/images/posts/{basename}"
        if slot in existing_by_id:
            row = dict(existing_by_id[slot])
            row["id"] = slot
            row["image"] = image_path
            rows.append(row)
            continue
        theme = PLANNED_THEME_BY_SLOT.get(
            slot,
            f"TODO: Theme for slot {slot}",
        )
        rows.append(
            {
                "id": slot,
                "theme": theme,
                "option": 1,
                "image": image_path,
                "content": stub_content(slot, theme),
            },
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge posts.json from PNG inventory.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary only (default if neither --write nor --dry-run).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write web/public/posts.json.",
    )
    args = parser.parse_args()
    if not args.write:
        args.dry_run = True

    slot_to_basename = png_slots_web()
    if not slot_to_basename:
        print(
            f"ERROR: No NN_Prompt_Anatomy.png files under {IMG_WEB}. "
            "Add PNGs or fix path.",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    existing_by_id: dict[int, dict] = {}
    for r in raw:
        existing_by_id[int(r["id"])] = dict(r)

    merged = build_merged_rows(existing_by_id, slot_to_basename)
    new_ids = {int(r["id"]) for r in merged}
    old_ids = set(existing_by_id.keys())
    dropped = sorted(old_ids - new_ids)
    added = sorted(new_ids - old_ids)

    print(f"PNG slots on disk: {len(slot_to_basename)}")
    print(f"Current posts.json rows: {len(raw)}")
    print(f"After merge rows: {len(merged)}")
    print(f"New slots (stub content): {len(added)} {added[:30]!r}{'…' if len(added) > 30 else ''}")
    print(f"Dropped post ids (no PNG for that slot): {len(dropped)} {dropped!r}")

    if args.write:
        POSTS_PATH.write_text(
            json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {POSTS_PATH}")
    else:
        print("(dry-run; use --write to save)")


if __name__ == "__main__":
    main()
