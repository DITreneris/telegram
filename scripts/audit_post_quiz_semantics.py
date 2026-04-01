"""Heuristic audit: post ↔ poll semantic hints (stub body, theme_note, question overlap).

Run from repo root:
  python scripts/audit_post_quiz_semantics.py

Read-only. Does not modify JSON. Use after editing ``posts.json`` / ``data/polls.json``.

Flags:
- ``generic_stub_body``: content still contains the standard expanded stub paragraph.
- ``theme_note_mismatch``: poll ``theme_note`` differs from post ``theme`` (when set).
- ``low_question_overlap``: for posts **without** the generic stub paragraph, Jaccard
  overlap between poll question and post theme+content is below a threshold (rough signal;
  stub bodies share identical tokens and are skipped for this metric).

See ``queue_manifest_sync.py`` for mechanical linking (``related_post_id``, order).
"""

from __future__ import annotations

import argparse
import json
import re
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "web" / "public" / "posts.json"
POLLS = ROOT / "data" / "polls.json"

# Fingerprint from fill_stub / merge workflows (long generic middle paragraph).
GENERIC_STUB_FINGERPRINT = "Most weak AI outputs come from vague asks"

_STOP = frozenset(
    """
    a an the and or but if in on at to for of as is it its this that these those
    you your we they them their our with from by be are was were been being
    not no so than then too also into about over after before when what which
    who how why all any each every both few more most other some such same
    will can could should would may might must do does did done having have has had
    i me my he she her him his ours
    """.split()
)


def _tokens(text: str) -> set[str]:
    raw = re.sub(r"http\S+", " ", text.lower())
    raw = raw.translate(str.maketrans("", "", string.punctuation.replace("-", "")))
    words = [w.strip("-") for w in raw.split() if len(w.strip("-")) > 1]
    return {w for w in words if w not in _STOP}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Heuristic post vs poll semantics audit.")
    parser.add_argument(
        "--overlap-threshold",
        type=float,
        default=0.08,
        help="Flag low_question_overlap when Jaccard(question, theme+content) is below this (default 0.08).",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass

    posts = json.loads(POSTS.read_text(encoding="utf-8"))
    poll_root = json.loads(POLLS.read_text(encoding="utf-8"))
    poll_items = poll_root.get("items", []) if isinstance(poll_root, dict) else []

    by_id: dict[int, dict] = {}
    for row in posts:
        if isinstance(row, dict) and isinstance(row.get("id"), int):
            by_id[int(row["id"])] = row

    lines: list[str] = []
    w = lines.append

    w("=== Generic stub body (fingerprint in content) ===")
    stub_ids: list[int] = []
    for pid in sorted(by_id):
        content = str(by_id[pid].get("content", ""))
        if GENERIC_STUB_FINGERPRINT in content:
            stub_ids.append(pid)
    w(f"  Post ids ({len(stub_ids)}): {stub_ids[:40]!r}{' …' if len(stub_ids) > 40 else ''}")
    w("")

    w("=== theme_note vs post.theme ===")
    mismatches: list[str] = []
    for p in poll_items:
        if not isinstance(p, dict):
            continue
        rid = p.get("related_post_id")
        if not isinstance(rid, int):
            continue
        tn = p.get("theme_note")
        if not isinstance(tn, str) or not tn.strip():
            continue
        row = by_id.get(rid)
        if not row:
            continue
        theme = str(row.get("theme", "")).strip()
        if theme != tn.strip():
            mismatches.append(f"  post {rid} poll {p.get('id')!r}: theme_note != theme")
    if mismatches:
        for m in mismatches[:30]:
            w(m)
        if len(mismatches) > 30:
            w(f"  … +{len(mismatches) - 30} more")
    else:
        w("  (all theme_note values match post.theme where theme_note is set)")
    w("")

    w(
        f"=== Low question overlap (non-stub posts only, Jaccard < {args.overlap_threshold}) ==="
    )
    low: list[str] = []
    skipped_stub = 0
    for p in poll_items:
        if not isinstance(p, dict):
            continue
        rid = p.get("related_post_id")
        q = p.get("question")
        if not isinstance(rid, int) or not isinstance(q, str) or not q.strip():
            continue
        row = by_id.get(rid)
        if not row:
            continue
        theme = str(row.get("theme", ""))
        content = str(row.get("content", ""))
        if GENERIC_STUB_FINGERPRINT in content:
            skipped_stub += 1
            continue
        q_tok = _tokens(q)
        post_tok = _tokens(theme + " " + content[:1200])
        jac = _jaccard(q_tok, post_tok)
        if jac < args.overlap_threshold:
            low.append(
                f"  post {rid} poll {p.get('id')!r}: jaccard={jac:.3f} theme={theme[:50]!r}…"
            )
    w(f"  Skipped {skipped_stub} polls (post body contains generic stub fingerprint).")
    if low:
        for m in low[:40]:
            w(m)
        if len(low) > 40:
            w(f"  … +{len(low) - 40} more")
    else:
        w("  (none below threshold)")
    w("")
    w("Note: overlap is a rough heuristic; template polls and punctuation skew scores.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
