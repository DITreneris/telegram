#!/usr/bin/env python3
"""One-shot: add topic_key to web/public/posts.json rows (known themes + slug fallback)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

KNOWN: dict[str, str] = {
    "Your AI isn't underperforming. You are.": "ai_mirror_inputs",
    'Stop saying "please" to your AI.': "please_vs_precision",
    "You're not prompting. You're guessing.": "guessing_vs_prompting",
    "This one mistake makes your AI outputs useless.": "define_output",
    "Your prompts are random → so are your results.": "random_prompts",
    "From random answers → to controlled outputs": "random_to_controlled",
    "You're one prompt away from 10x better results.": "one_prompt_10x",
    "Same prompt vs structured prompt (before/after)": "before_after_structure",
    "The mistake 90% of AI users make": "mistake_90_percent",
    "How I turned AI from toy → system": "toy_to_system",
}


def fallback_key(theme: str) -> str:
    s = theme.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s[:80] if s else "topic"


def main() -> int:
    path = _REPO_ROOT / "web" / "public" / "posts.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        print("error: posts.json must be a list", file=sys.stderr)
        return 1
    for r in rows:
        if not isinstance(r, dict) or "theme" not in r:
            continue
        th = str(r["theme"])
        r["topic_key"] = KNOWN.get(th, fallback_key(th))
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path} ({len(rows)} rows).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
