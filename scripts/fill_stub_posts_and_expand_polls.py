"""Fill TODO stub rows in posts.json and add one poll per post in data/polls.json.

Run from repo root after merge_posts_json_from_png.py:
  python scripts/fill_stub_posts_and_expand_polls.py

Uses themes from gen_post_images_gap_report.PLANNED_THEME_BY_SLOT plus SLOT_THEMES
for slots that exist on disk but were not in the planning dict.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from gen_post_images_gap_report import PLANNED_THEME_BY_SLOT  # noqa: E402

POSTS_PATH = ROOT / "web" / "public" / "posts.json"
POLLS_PATH = ROOT / "data" / "polls.json"

# queue_manifest_sync / Telegram limits
MAX_Q = 300
MAX_OPT = 100
MAX_NOTE = 500

# Headlines for PNG slots not covered by PLANNED_THEME_BY_SLOT (74-card deck subset).
SLOT_THEMES: dict[int, str] = {
    32: "Stack your prompt: input, context, reasoning, quality gates.",
    33: "You're not prompting. You're guessing. (ICQRA edition)",
    34: "Models comply—they don't think. Design for that.",
    36: "How a Content Creator uses AI: decisions & stack",
    37: "Role + deliverable beats “write something catchy.”",
    38: "Templates beat one-off vibes for repeated work.",
    39: "Shipping weekly? Use a repeatable prompt system.",
    41: "Sharper drafts start with explicit success criteria.",
    42: "Boring prompts win when the work is serious.",
    43: "If the output drifts, tighten constraints—not the model.",
    44: "The layered prompt: burger, not soup (stack your ask).",
    46: "One clear job per prompt; split multi-part work.",
    47: "Give examples when format matters.",
    48: "Say what “done” looks like before you ask.",
    49: "Risky tasks need red-team style constraints.",
    51: "Long tasks: outline first, then expand.",
    52: "Short wins: precision over personality.",
    53: "Don't confuse fluency with correctness.",
    54: "Reuse winning prompts like code snippets.",
    56: "Measure output against your rubric, not vibes.",
    58: "When stuck, restate role and constraints—then retry.",
    59: "Parallel drafts: vary constraints, not models.",
    60: "Build a library of proven prompts for your role.",
    62: "Safety and tone live in the spec, not the vibe.",
    64: "Structured debriefs turn chats into playbooks.",
    65: "Tool choice matters less than prompt design.",
    70: "Pick tools after you know the job-to-be-done.",
    71: "Skepticism is healthy—test prompts like experiments.",
    74: "From slide outline to narrative: sequence matters.",
    75: "Operations rhythm: same stack, clearer prompts.",
    76: "Don't outsource judgment—prompt for options, you decide.",
    81: "Code + AI: keep specs in sync with prompts.",
    84: "Builders ship when prompts encode acceptance checks.",
    86: "Specialists win with narrow, testable asks.",
    89: "Review AI like a PM: scope, acceptance, risks.",
    93: "Late-stage polish: shorten, sharpen, add proof.",
    94: "Keep CTAs explicit—models hedge by default.",
    95: "One audience per message; split multi-audience work.",
    96: "Numbers and dates need an explicit ask or they blur.",
    97: "Lists work when you cap length and order.",
    98: "Stories need arc: hook, tension, payoff.",
    99: "Close loops: ask for next step or CTA.",
    100: "You're not prompting. You're guessing. (short stack edition)",
}

OPT_WEAK = "Casual open ask with no role, format, or constraints."
OPT_STRONG = "Role, audience, task, output shape, and explicit constraints."

assert len(OPT_WEAK) <= MAX_OPT and len(OPT_STRONG) <= MAX_OPT


def resolve_theme(pid: int, current: str) -> str:
    s = current.strip()
    if s.startswith("TODO:") or "TODO: Theme for slot" in s:
        return (
            PLANNED_THEME_BY_SLOT.get(pid)
            or SLOT_THEMES.get(pid)
            or f"Prompt anatomy card {pid}: structure beats vague asks."
        ).strip()
    return s


def body_for_theme(theme: str) -> str:
    return (
        f"📌 {theme}\n\n"
        "Most weak AI outputs come from vague asks. The model fills gaps with generic safe text.\n\n"
        "Fix it by naming the role, the audience, the output shape, and the constraints. "
        "That turns a chat into a brief—and the model stops improvising in the wrong direction.\n\n"
        "🎯 Same model, clearer instructions → sharper deliverables.\n\n"
        "→ https://promptanatomy.app\n"
    )


def poll_question_for(pid: int) -> str:
    base = f"Post #{pid}: which input reflects structured professional prompting?"
    if len(base) > MAX_Q:
        return base[: MAX_Q - 3].rstrip() + "..."
    return base


def poll_note(theme: str) -> str:
    t = theme.strip()
    if len(t) <= MAX_NOTE:
        return t
    return t[: MAX_NOTE - 3].rstrip() + "..."


def main() -> None:
    posts = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    for row in posts:
        pid = int(row["id"])
        theme = resolve_theme(pid, str(row.get("theme", "")))
        row["theme"] = theme
        c = str(row.get("content", ""))
        if "TODO: Replace" in c or "TODO: Theme for slot" in c:
            row["content"] = body_for_theme(theme)

    post_ids = sorted(int(r["id"]) for r in posts)
    raw_polls = json.loads(POLLS_PATH.read_text(encoding="utf-8"))
    items = list(raw_polls.get("items", []))
    seen: set[int] = set()
    for it in items:
        seen.add(int(it["related_post_id"]))

    next_idx = len(items) + 1
    for pid in post_ids:
        if pid in seen:
            continue
        q = poll_question_for(pid)
        theme = next((str(r["theme"]) for r in posts if int(r["id"]) == pid), "")
        items.append(
            {
                "id": f"poll_post_{pid:03d}_structure",
                "related_post_id": pid,
                "question": q,
                "options": [OPT_WEAK, OPT_STRONG],
                "correct_option_id": 1,
                "theme_note": poll_note(theme),
            }
        )
        seen.add(pid)
        next_idx += 1

    raw_polls["items"] = items
    POLLS_PATH.write_text(
        json.dumps(raw_polls, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    POSTS_PATH.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {POSTS_PATH} ({len(posts)} posts)")
    print(f"Wrote {POLLS_PATH} ({len(items)} poll items)")


if __name__ == "__main__":
    main()
