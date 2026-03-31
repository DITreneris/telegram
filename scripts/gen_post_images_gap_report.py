"""Write docs/POST_IMAGES_GAP_1_100.md — PNG slots 1..100 vs web/public/images/posts.

Convention: filename is f"{n:02d}_Prompt_Anatomy.png" for n in 1..100
(Python formats 100 as "100").

Run from repo root: python scripts/gen_post_images_gap_report.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_PATH = ROOT / "web" / "public" / "posts.json"
IMG_WEB = ROOT / "web" / "public" / "images" / "posts"
OUT_PATH = ROOT / "docs" / "POST_IMAGES_GAP_1_100.md"

# Themes for slots not present in current posts.json (planning / former MISSING_POST_IMAGES briefs).
PLANNED_THEME_BY_SLOT: dict[int, str] = {
    31: "Most people are using the wrong AI image tool.",
    35: "Top AI text-to-video tools (2026)",
    40: "Which AI app for real work? (2026 tiers)",
    45: "Multimodal AI: images, PDFs, screenshots (2026)",
    50: "Audio AI: speech ↔ text (2026)",
    55: "Text → music AI (2026, short)",
    57: "Agreement is not intelligence. It's compliance.",
    61: "How a Researcher uses AI: decisions & stack",
    66: "How a Data Analyst uses AI: decisions & stack",
    72: "How a CMO uses AI: decisions & stack",
    77: "How Operations uses AI: decisions & stack",
    80: "Vibe coding: idea → MVP → ship (2026)",
    82: "How a Software Engineer uses AI: decisions & stack",
    85: "AI app builders: MVP → real app (2026)",
    87: "How a CTO uses AI: decisions & stack",
    90: "The stack that actually ships products (2026); shared template for several role posts in JSON",
}


def png_web() -> set[str]:
    if not IMG_WEB.is_dir():
        return set()
    return {p.name for p in IMG_WEB.glob("*.png")}


def slot_filename(n: int) -> str:
    return f"{n:02d}_Prompt_Anatomy.png"


def esc_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    rows = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    theme_by_id: dict[int, str] = {int(r["id"]): str(r["theme"]).strip() for r in rows}

    web = png_web()
    missing: list[int] = []
    present: list[int] = []
    for n in range(1, 101):
        fn = slot_filename(n)
        if fn in web:
            present.append(n)
        else:
            missing.append(n)

    lines = [
        "# Post PNG padengimas 1–100 (`web/public/images/posts`)",
        "",
        "Konvencija: failo vardas `NN_Prompt_Anatomy.png`, kur `NN` = `f\"{n:02d}\"` (1→`01` … 9→`09`, 100→`100`).",
        "",
        f"**Šaltinis:** [`web/public/posts.json`](../web/public/posts.json) (dabar **{len(rows)}** eilučių — ne visi slotai 1–100 turi `theme` JSON'e).",
        "",
        "## Santrauka",
        "",
        "| Rodiklis | Reikšmė |",
        "|----------|---------|",
        f"| Slotų iš viso (1–100) | 100 |",
        f"| PNG yra `web/public/images/posts/` | **{len(present)}** |",
        f"| PNG **trūksta** | **{len(missing)}** |",
        "",
        "## Trūkstami failai ir temos",
        "",
        "Tema: pirmiausia `posts.json` pagal posto `id` = slotui; jei nėra eilutės — `PLANNED_THEME_BY_SLOT` skripte; kitaip — *nėra įrašo*.",
        "",
        "| Slot | Failas | Tema | Pastaba |",
        "|------|--------|------|---------|",
    ]

    for n in missing:
        fn = slot_filename(n)
        if n in theme_by_id:
            theme = theme_by_id[n]
            note = "`posts.json`"
        elif n in PLANNED_THEME_BY_SLOT:
            theme = PLANNED_THEME_BY_SLOT[n]
            note = "planas (`scripts/gen_post_images_gap_report.py`)"
        else:
            theme = "—"
            note = "įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT`"

        lines.append(
            f"| {n} | `{fn}` | {esc_cell(theme)} | {note} |"
        )

    lines.extend(
        [
            "",
            "## Atnaujinimas",
            "",
            "```bash",
            "python scripts/gen_post_images_gap_report.py",
            "```",
            "",
            "## Related",
            "",
            "- [`POST_IMAGES.md`](POST_IMAGES.md)",
            "- [`MISSING_POST_IMAGES.md`](MISSING_POST_IMAGES.md)",
            "",
        ]
    )

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH} (missing {len(missing)} / 100)")


if __name__ == "__main__":
    main()
