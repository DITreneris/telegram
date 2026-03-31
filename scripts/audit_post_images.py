"""Image coverage vs posts.json. Checks web/public (Vite UI) and optional data/images.

Run from repo root: python scripts/audit_post_images.py

Printed **canonical inventory** uses fixed definitions so counts stay comparable run-to-run:
  A — rows in posts.json
  B — distinct post ids (must equal A)
  C — distinct image basenames referenced by posts
  D — *.png count under web/public/images/posts
  E — *.png count under data/images
  F — posts whose image resolves under web (can be C if all refs exist; can be A if reuse)

Separate planning metric (not equal to A): slots 1..100 vs NN_Prompt_Anatomy.png — see
  python scripts/gen_post_images_gap_report.py  -> docs/POST_IMAGES_GAP_1_100.md
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "web" / "public" / "posts.json"
IMG_WEB = ROOT / "web" / "public" / "images" / "posts"
IMG_DATA = ROOT / "data" / "images"


def png_set(folder: Path) -> set[str]:
    if not folder.is_dir():
        return set()
    return {p.name for p in folder.glob("*.png")}


def main() -> None:
    rows = json.loads(POSTS.read_text(encoding="utf-8"))
    web = png_set(IMG_WEB)
    data = png_set(IMG_DATA)
    union = web | data

    ids = [int(r["id"]) for r in rows]
    id_dupes = [k for k, v in Counter(ids).items() if v > 1]

    by_basename: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        name = r["image"].rsplit("/", 1)[-1]
        by_basename[name].append(int(r["id"]))
    reused = {b: pids for b, pids in by_basename.items() if len(pids) > 1}

    unique_need = set(by_basename.keys())

    ok_web, ok_data_only, missing = [], [], []
    for r in rows:
        name = r["image"].rsplit("/", 1)[-1]
        if name in web:
            ok_web.append(r["id"])
        elif name in data:
            ok_data_only.append((r["id"], name))
        else:
            missing.append((r["id"], name))

    extra_web = web - unique_need

    print("=== Canonical inventory (fixed definitions) ===")
    print(f"  A  posts.json rows (objects):     {len(rows)}")
    print(f"  B  distinct post id:              {len(set(ids))}" + ("  ERROR: duplicate ids" if id_dupes else ""))
    print(f"  C  distinct image basenames:      {len(unique_need)}  (<= A if one image reused by multiple posts)")
    print(f"  D  PNG files web/.../posts:       {len(web)}")
    print(f"  E  PNG files data/images:         {len(data)}")
    print(f"  F  posts with image on WEB path: {len(ok_web)}  (of {len(rows)} rows)")
    print(f"  G  JSON refs missing on web:      {len(missing)}")
    print(f"  H  JSON refs only in data:        {len(ok_data_only)}")
    print(f"  I  WEB PNGs not referenced by JSON: {len(extra_web)}  (D - C when web superset; exact when no reuse)")
    print()
    if web != data:
        print("NOTE: web and data PNG sets differ (symmetric diff):")
        for n in sorted(web - data):
            print(f"  only web:  {n}")
        for n in sorted(data - web):
            print(f"  only data: {n}")
        print()
    else:
        print("NOTE: web and data PNG basenames are identical (same count).")
        print()
    if reused:
        print("Image reuse (same basename, multiple post ids):")
        for b in sorted(reused.keys()):
            print(f"  {b} -> ids {sorted(reused[b])}")
        print()
    print("Interpretation:")
    print("  A vs D: archive can hold more cards than current posts.json lists.")
    print("  A vs C: if C < A, at least one PNG is shared by two or more posts.")
    print("  Planning deck 1..100: run  python scripts/gen_post_images_gap_report.py")
    print()

    print("=== Detail ===")
    print(f"Union (web | data) unique basenames: {len(union)}")
    print(f"Distinct filenames in JSON satisfied via union: {len(unique_need & union)}")
    print(f"Still absent (need asset): {len(unique_need - union)}")
    if ok_data_only:
        print("\nIn data/images but not web/public - UI will 404 until copied:")
        for pid, name in ok_data_only:
            print(f"  id {pid}: {name}")
    if extra_web:
        print(f"\nExtra PNGs in web/public (not in posts.json references), {len(extra_web)} files:")
        for n in sorted(extra_web):
            print(f"  - {n}")
    if missing:
        print("\nMissing everywhere (need asset):")
        for pid, name in missing[:25]:
            print(f"  id {pid}: {name}")
        if len(missing) > 25:
            print(f"  ... and {len(missing) - 25} more")


if __name__ == "__main__":
    main()
