"""Write docs/MISSING_POST_IMAGES.md - PNG briefs vs posts.json + web + data/images.

Run from repo root: python scripts/gen_missing_post_images_md.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_PATH = ROOT / "web" / "public" / "posts.json"
OUT_PATH = ROOT / "docs" / "MISSING_POST_IMAGES.md"
IMG_WEB = ROOT / "web" / "public" / "images" / "posts"
IMG_DATA = ROOT / "data" / "images"


def png_set(folder: Path) -> set[str]:
    if not folder.is_dir():
        return set()
    return {p.name for p in folder.glob("*.png")}


def esc_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    rows = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    web = png_set(IMG_WEB)
    data = png_set(IMG_DATA)
    union = web | data

    data_only: list[tuple[int, str, str]] = []
    missing: list[tuple[int, str, str]] = []
    for r in rows:
        name = r["image"].rsplit("/", 1)[-1]
        tid, theme = r["id"], r["theme"]
        if name in web:
            continue
        if name in data:
            data_only.append((tid, name, theme))
        else:
            missing.append((tid, name, theme))

    by_file: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for tid, name, theme in missing:
        by_file[name].append((tid, theme))

    lines = [
        "# Trūkstami `posts.json` PNG: failai ir temos",
        "",
        "Šaltinis: [`web/public/posts.json`](../web/public/posts.json). Katalogai: [`web/public/images/posts/`](../web/public/images/posts/) (UI), [`data/images/`](../data/images/).",
        "",
        "Atnaujinti: `python scripts/gen_missing_post_images_md.py`",
        "",
        "## 1. Failo **nėra** diske (nei web, nei data) – sukurti",
        "",
        "| Failas | Post `id` | Theme (iš JSON) |",
        "|--------|-----------|-------------------|",
    ]

    for fname in sorted(by_file.keys()):
        posts = sorted(by_file[fname], key=lambda x: x[0])
        ids = ", ".join(str(i) for i, _ in posts)
        themes = "<br>".join(f"**{i}:** {esc_cell(th)}" for i, th in posts)
        lines.append(f"| `{fname}` | {ids} | {themes} |")

    lines.extend(
        [
            "",
            "**Vizualinė kryptis:** ant kortelės – posto `theme` tekstas (EN); Prompt Anatomy stilius: struktūra, sluoksniai, kontrolė, „system not toy“. `90_Prompt_Anatomy.png` – vienas bendras „įrankių / stack / sluoksnių“ šablonas visiems jį naudojantiems įrašams.",
            "",
            "## 2. Yra tik `data/images` – nukopijuok į `web/public/images/posts`",
            "",
            "Failai jau egzistuoja; naršyklė jų nerodys, kol nėra `web/public` kopijoje.",
            "",
            "| Failas | Post `id` | Theme |",
            "|--------|-----------|-------|",
        ]
    )
    for tid, fname, theme in sorted(data_only, key=lambda x: (x[1], x[0])):
        lines.append(f"| `{fname}` | {tid} | {esc_cell(theme)} |")

    lines.extend(["", "## Related", "", "- [`POST_IMAGES.md`](POST_IMAGES.md)", ""])

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
