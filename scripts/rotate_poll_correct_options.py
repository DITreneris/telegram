#!/usr/bin/env python3
"""Alternate correct_option_id 0/1 for 2-option polls by post order (reduces position bias)."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POLLS = REPO / "data" / "polls.json"


def main() -> None:
    data = json.loads(POLLS.read_text(encoding="utf-8"))
    items = data["items"]
    sorted_ids = sorted(item["related_post_id"] for item in items)
    pos = {pid: i for i, pid in enumerate(sorted_ids)}

    for item in items:
        opts = item.get("options") or []
        if len(opts) != 2:
            continue
        cid = item["correct_option_id"]
        if cid not in (0, 1):
            continue
        correct = opts[cid]
        wrong = opts[1 - cid]
        i = pos[item["related_post_id"]]
        want_correct_first = i % 2 == 0
        if want_correct_first:
            item["options"] = [correct, wrong]
            item["correct_option_id"] = 0
        else:
            item["options"] = [wrong, correct]
            item["correct_option_id"] = 1

    POLLS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", POLLS)


if __name__ == "__main__":
    main()
