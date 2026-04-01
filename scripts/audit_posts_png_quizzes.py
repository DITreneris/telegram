"""Audit: posts.json vs PNG files vs polls.json (1:1 id↔slot principle).

Run from repo root:
  python scripts/audit_posts_png_quizzes.py
  python scripts/audit_posts_png_quizzes.py --write-inventory docs/CONTENT_INVENTORY.md

Exit code **1** if canonical integrity breaks (duplicate ids, id/slot/filename mismatch,
same PNG basename reused by multiple posts, polls pointing at unknown posts, duplicate
quiz `related_post_id`, missing image files, or JSON image only under `data/images`
but not mirrored on `web/public/images/posts/`). Warnings such as extra PNG files
without a post row, or posts without a quiz, still exit **0** — fix those in content
workflows but they do not fail CI.

See also: scripts/audit_post_images.py (canonical A–I labels).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "web" / "public" / "posts.json"
IMG_WEB = ROOT / "web" / "public" / "images" / "posts"
IMG_DATA = ROOT / "data" / "images"
POLLS = ROOT / "data" / "polls.json"

PNG_NAME_RE = re.compile(r"^(\d+)_Prompt_Anatomy\.png$")


def png_set(folder: Path) -> set[str]:
    if not folder.is_dir():
        return set()
    return {p.name for p in folder.glob("*.png")}


def slot_from_basename(name: str) -> int | None:
    m = PNG_NAME_RE.match(name)
    return int(m.group(1)) if m else None


def load_posts() -> list[dict]:
    return json.loads(POSTS.read_text(encoding="utf-8"))


def load_poll_items() -> list[dict]:
    raw = json.loads(POLLS.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1:
        return []
    items = raw.get("items")
    return items if isinstance(items, list) else []


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit posts vs PNG vs polls.")
    parser.add_argument(
        "--write-inventory",
        type=Path,
        metavar="PATH",
        help="Write markdown summary to PATH (e.g. docs/CONTENT_INVENTORY.md).",
    )
    args = parser.parse_args()

    rows = load_posts()
    web = png_set(IMG_WEB)
    data = png_set(IMG_DATA)
    poll_items = load_poll_items()

    ids = [int(r["id"]) for r in rows]
    id_dupes = [k for k, v in Counter(ids).items() if v > 1]

    by_basename: dict[str, list[int]] = defaultdict(list)
    id_to_basename: dict[int, str] = {}
    principle_mismatch: list[str] = []
    for r in rows:
        pid = int(r["id"])
        path = str(r.get("image", ""))
        name = path.rsplit("/", 1)[-1] if path else ""
        by_basename[name].append(pid)
        id_to_basename[pid] = name
        slot = slot_from_basename(name)
        if slot is None and name:
            principle_mismatch.append(
                f"id {pid}: image basename {name!r} is not NN_Prompt_Anatomy.png",
            )
        elif slot is not None and slot != pid:
            principle_mismatch.append(
                f"id {pid}: image slot {slot} from filename != post id {pid} ({name})",
            )

    reused = {b: pids for b, pids in by_basename.items() if len(pids) > 1 and b}
    unique_need = set(by_basename.keys()) - {""}

    ok_web, ok_data_only, missing_file = [], [], []
    for r in rows:
        name = str(r.get("image", "")).rsplit("/", 1)[-1]
        pid = int(r["id"])
        if name in web:
            ok_web.append(pid)
        elif name in data:
            ok_data_only.append((pid, name))
        elif name:
            missing_file.append((pid, name))

    extra_web = web - unique_need

    slots_with_png = sorted(
        s for s in (slot_from_basename(n) for n in web) if s is not None
    )
    post_ids = set(ids)
    png_slots = set(slots_with_png)
    posts_without_png_on_disk = sorted(post_ids - png_slots)
    png_without_post_row = sorted(png_slots - post_ids)

    # Polls
    related_ids = [int(p["related_post_id"]) for p in poll_items if "related_post_id" in p]
    rel_dupes = [k for k, v in Counter(related_ids).items() if v > 1]
    post_ids_with_poll = set(related_ids)
    posts_missing_quiz = sorted(post_ids - post_ids_with_poll)
    polls_orphan = sorted(post_ids_with_poll - post_ids)

    lines: list[str] = []
    w = lines.append

    w("=== Canonical inventory (same labels as audit_post_images.py) ===")
    w(f"  A  posts.json rows:                {len(rows)}")
    w(
        f"  B  distinct post id:             {len(set(ids))}"
        + ("  ERROR: duplicate ids" if id_dupes else ""),
    )
    w(f"  C  distinct image basenames:       {len(unique_need)}")
    w(f"  D  PNG files web/.../posts:        {len(web)}")
    w(f"  E  PNG files data/images:          {len(data)}")
    w(f"  F  posts with image on WEB path:   {len(ok_web)}  (of {len(rows)})")
    w(f"  G  JSON refs missing on web:       {len(missing_file)}")
    w(f"  H  JSON refs only in data:         {len(ok_data_only)}")
    w(f"  I  WEB PNGs not referenced by JSON: {len(extra_web)}")
    w("")
    w("=== 1:1 principle (id == slot from NN_Prompt_Anatomy.png) ===")
    if principle_mismatch:
        for msg in principle_mismatch:
            w(f"  MISMATCH: {msg}")
    else:
        w("  (no id/slot/filename mismatches for valid basenames)")
    if reused:
        w("  Same basename used by multiple post ids:")
        for b in sorted(reused.keys()):
            w(f"    {b} -> ids {sorted(reused[b])}")
    else:
        w("  (no multi-post reuse of same basename)")
    w("")
    w("=== PNG set vs post id set ===")
    w(f"  Slots with a PNG file (count):     {len(png_slots)}")
    w(f"  Post rows whose id has no PNG:     {len(posts_without_png_on_disk)}  {posts_without_png_on_disk[:20]!r}{'…' if len(posts_without_png_on_disk) > 20 else ''}")
    w(f"  PNG files with no post id row:     {len(png_without_post_row)}  {png_without_post_row[:20]!r}{'…' if len(png_without_post_row) > 20 else ''}")
    w("")
    w("=== polls.json (quiz bank) ===")
    w(f"  Poll items:                        {len(poll_items)}")
    w(f"  Duplicate related_post_id:         {rel_dupes if rel_dupes else 'none'}")
    w(f"  Post ids with at least one poll:   {len(post_ids_with_poll)}")
    w(f"  Post ids without any poll:         {len(posts_missing_quiz)}")
    if polls_orphan:
        w(f"  Poll related_post_id missing in posts.json: {polls_orphan}")
    w("")
    w("Commands: python scripts/audit_post_images.py")
    w("          python scripts/gen_post_images_gap_report.py")
    w("          python scripts/merge_posts_json_from_png.py --dry-run")
    w("")

    text = "\n".join(lines)
    print(text, end="")

    if args.write_inventory:
        inv_path = args.write_inventory
        if not inv_path.is_absolute():
            inv_path = ROOT / inv_path
        inv_path.parent.mkdir(parents=True, exist_ok=True)
        md = [
            "# Content inventory (posts, PNG, quizzes)",
            "",
            "Auto-generated by `python scripts/audit_posts_png_quizzes.py --write-inventory docs/CONTENT_INVENTORY.md`.",
            "Re-run after changing `posts.json`, `web/public/images/posts/`, or `data/polls.json`.",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| posts.json rows (A) | {len(rows)} |",
            f"| PNG on `web/public/images/posts/` (D) | {len(web)} |",
            f"| Distinct image basenames in JSON (C) | {len(unique_need)} |",
            f"| Poll items in `data/polls.json` | {len(poll_items)} |",
            f"| Post ids with no PNG file (orphan rows vs disk) | {len(posts_without_png_on_disk)} |",
            f"| PNG slots with no post row (before merge) | {len(png_without_post_row)} |",
            "",
            "## Principle",
            "",
            "Target: one row per `NN_Prompt_Anatomy.png` on disk, with `id == NN` and "
            "`image` = `/images/posts/NN_Prompt_Anatomy.png`. Run "
            "`python scripts/merge_posts_json_from_png.py --write` to align.",
            "",
            "## Quiz coverage",
            "",
            f"- Posts without any linked poll: **{len(posts_missing_quiz)}** (see audit stdout for ids).",
            "- Full 1:1 quiz coverage is optional; add rows to `data/polls.json` when content is ready.",
            "",
            "## Raw audit",
            "",
            "```",
            text.rstrip(),
            "```",
            "",
        ]
        inv_path.write_text("\n".join(md), encoding="utf-8")
        print(f"Wrote {inv_path}")

    fatal = bool(
        id_dupes
        or principle_mismatch
        or reused
        or rel_dupes
        or polls_orphan
        or missing_file
        or ok_data_only
    )
    if fatal:
        print(
            "\nAUDIT FAILED: fix posts.json / web PNG / data PNG mirror / polls.json "
            "(see errors above).",
            file=sys.stderr,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
