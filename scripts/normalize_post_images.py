"""Crop to 16:9, resize to 1600x900, optimize PNGs in data/images; copy to web/public/images/posts."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install Pillow: pip install Pillow", file=sys.stderr)
    raise

TARGET_W = 1600
TARGET_H = 900
TARGET_RATIO = TARGET_W / TARGET_H


def crop_to_16_9(img: Image.Image) -> Image.Image:
    w, h = img.size
    if h == 0:
        return img
    ratio = w / h
    if abs(ratio - TARGET_RATIO) < 1e-6:
        return img
    if ratio > TARGET_RATIO:
        new_w = int(round(h * TARGET_RATIO))
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(round(w / TARGET_RATIO))
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    src_dir = root / "data" / "images"
    pub_dir = root / "web" / "public" / "images" / "posts"
    if not src_dir.is_dir():
        print(f"Missing directory: {src_dir}", file=sys.stderr)
        sys.exit(1)
    pub_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.png"))
    if len(files) != 30:
        print(f"Expected 30 PNG files, found {len(files)} in {src_dir}", file=sys.stderr)
        sys.exit(1)

    for path in files:
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            cropped = crop_to_16_9(rgb)
            out = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
            out.save(path, format="PNG", optimize=True, compress_level=9)
        dest = pub_dir / path.name
        shutil.copy2(path, dest)
        print(f"OK {path.name} -> {TARGET_W}x{TARGET_H}", flush=True)

    print(f"Copied {len(files)} files to {pub_dir}", flush=True)


if __name__ == "__main__":
    main()
