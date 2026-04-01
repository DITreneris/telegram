"""Restore web/public/posts.json themes (and bodies) to the PNG-slot headline map.

Uses the same headlines as ``SLOT_THEMES`` / ``PLANNED_THEME_BY_SLOT`` in
``fill_stub_posts_and_expand_polls.py`` + ``gen_post_images_gap_report.py`` —
the deck titles aligned to ``NN_Prompt_Anatomy.png`` slot numbers.

Post **31** keeps the tool-picker body (matches \"wrong image tool\" headline).
Other slots **31+** use ``body_for_theme`` (short educational stub).

Then: sync poll ``theme_note`` from headlines, re-apply ``apply_poll_lesson_patches``,
regenerate ``data/content.json`` (run those steps after this script).

Usage (repo root)::

    python scripts/restore_posts_png_aligned.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from fill_stub_posts_and_expand_polls import (  # noqa: E402
    SLOT_THEMES,
    body_for_theme,
    poll_note,
)
from gen_post_images_gap_report import PLANNED_THEME_BY_SLOT  # noqa: E402

POSTS_PATH = ROOT / "web" / "public" / "posts.json"
POLLS_PATH = ROOT / "data" / "polls.json"

# Matches data/content.generated.json post_031_text (headline = PLANNED slot 31).
CONTENT_31_TOOL_LIST = """🖼️ Wrong image AI? Usually a random pick—not "bad" tools.

By job:
OpenAI / ChatGPT — https://chatgpt.com · accuracy, edits
Midjourney — https://www.midjourney.com · look & mood
Firefly — https://www.adobe.com/products/firefly.html · Adobe workflows
Gemini — https://gemini.google.com · Google stack
FLUX — https://blackforestlabs.ai · control, APIs
Ideogram — https://ideogram.ai · text inside images

✅ TL;DR: accuracy→OpenAI · beauty→MJ · workflow→Firefly · Google→ease · control→FLUX · type→Ideogram

Best for what—not "best overall"? Which do you use?
https://promptanatomy.app"""


def headline_for_slot(pid: int, current_theme: str) -> str | None:
    """Return canonical headline if this slot is in the PNG-aligned maps."""
    if pid in SLOT_THEMES:
        return SLOT_THEMES[pid]
    if pid in PLANNED_THEME_BY_SLOT:
        return PLANNED_THEME_BY_SLOT[pid]
    return None


def main() -> None:
    posts = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    n_theme = 0
    n_body = 0
    for row in posts:
        pid = int(row["id"])
        new_theme = headline_for_slot(pid, str(row.get("theme", "")))
        if new_theme is None:
            continue
        if row.get("theme") != new_theme:
            row["theme"] = new_theme
            n_theme += 1
        row.pop("topic_key", None)
        if pid == 31:
            body = CONTENT_31_TOOL_LIST
        elif pid >= 31:
            body = body_for_theme(new_theme)
        else:
            continue
        if row.get("content") != body:
            row["content"] = body
            n_body += 1

    POSTS_PATH.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {POSTS_PATH}: theme updates {n_theme}, body updates {n_body}")

    theme_by_id = {int(r["id"]): str(r["theme"]).strip() for r in posts}
    pdata = json.loads(POLLS_PATH.read_text(encoding="utf-8"))
    n_poll = 0
    for item in pdata.get("items", []):
        rid = item.get("related_post_id")
        if not isinstance(rid, int):
            continue
        th = theme_by_id.get(rid)
        if not th:
            continue
        note = poll_note(th)
        if item.get("theme_note") != note:
            item["theme_note"] = note
            n_poll += 1
    POLLS_PATH.write_text(json.dumps(pdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {POLLS_PATH}: theme_note updates {n_poll}")

    subprocess.run(
        [sys.executable, str(_SCRIPTS / "apply_poll_lesson_patches.py")],
        cwd=str(ROOT),
        check=True,
    )
    print("Ran apply_poll_lesson_patches.py")

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_queue_from_posts.py"), "--in-place"],
        cwd=str(ROOT),
        check=True,
    )
    print("Ran sync_queue_from_posts.py --in-place")


if __name__ == "__main__":
    main()
