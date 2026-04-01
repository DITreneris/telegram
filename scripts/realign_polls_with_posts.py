"""After sync_posts_json_from_generated_manifest.py, fix quiz copy in data/polls.json.

Role-stack posts share one lesson question; other restored ids get a short tailored pair.
Run from repo root: python scripts/realign_polls_with_posts.py
"""

from __future__ import annotations

import json
from pathlib import Path

# Post ids whose theme is "How … uses AI: decisions & stack" (order matches posts.json)
ROLE_STACK_IDS: frozenset[int] = frozenset(
    {
        32,
        37,
        41,
        46,
        51,
        56,
        66,
        71,
        76,
        81,
        86,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
    }
)

ROLE_STACK_POLL = (
    "The post says pros should prioritize what over collecting more AI apps?",
    [
        "A longer menu of tools and browser tabs.",
        "Clear decisions and a repeatable layered workflow.",
    ],
    1,
)

# related_post_id -> (question, [opt0, opt1], correct_option_id)
TAILORED: dict[int, tuple[str, list[str], int]] = {
    33: (
        "You're guessing when the model has to invent which missing layers?",
        [
            "You give instruction, context, query, rules, and how you'll judge output.",
            "You drop one vague sentence and hope it reads your mind.",
        ],
        0,
    ),
    34: (
        "The post reframes AI as a system. What does that imply?",
        [
            "Chat casually; the model will infer the full workflow.",
            "Design layers: input, context, reasoning, quality, output—like a pipeline.",
        ],
        1,
    ),
    36: (
        "If AI keeps agreeing with you, what did you probably fail to add?",
        [
            "More compliments in the prompt.",
            "Pressure: criteria, pushback, and standards so it can't only validate.",
        ],
        1,
    ),
    38: (
        "You don't want better AI; you want less thinking. What's the risk?",
        [
            "You front-load clear constraints so outputs work first time.",
            "You copy-paste outputs without structure—and skip real thinking.",
        ],
        1,
    ),
    39: (
        "Most users stay unstructured. What breaks that cycle?",
        [
            "Random one-off prompts every time.",
            "Role, task, context, constraints, format, and evaluation as a system.",
        ],
        1,
    ),
    42: (
        "AI didn't replace your brain. You stopped using it. Best fix?",
        [
            "Let AI think so you don't have to.",
            "Use AI to think harder: verify, structure, and challenge outputs.",
        ],
        1,
    ),
    43: (
        '"You\'re feeding it" means what in practice?',
        [
            "You give vague asks so it adapts down to average.",
            "You starve the model of data on purpose.",
        ],
        0,
    ),
    44: (
        "Prompts fail for one simple reason in the post. Which?",
        [
            "The model is outdated.",
            "They skip structured layers (input, context, reasoning, quality, output).",
        ],
        1,
    ),
    47: (
        "AI respects pressure, not politeness. What should you add?",
        [
            "More 'please' and 'maybe' so it stays gentle.",
            "Explicit quality bar, criteria, and pushback—not soft asks only.",
        ],
        1,
    ),
    48: (
        "AI revealed your level. What creates the gap between users?",
        [
            "Which logo is on the homepage.",
            "How you structure, set standards, and control the ask.",
        ],
        1,
    ),
    49: (
        "AI doesn't think; it follows you. So weak outputs usually mean:",
        [
            "The weights are wrong.",
            "Your direction, standards, and prompts are weak or vague.",
        ],
        1,
    ),
    52: (
        "Polite prompts get polite answers—not better ones. Better pattern?",
        [
            "Soften every instruction so the model feels safe.",
            "Be precise and demanding: criteria, limits, and expected shape.",
        ],
        1,
    ),
    53: (
        "AI doesn't know you—it knows your patterns. Leverage that how?",
        [
            "Keep vague habits so it mirrors them.",
            "Upgrade inputs and standards so the mirror improves.",
        ],
        1,
    ),
    54: (
        "Good prompts are built, not written. What does 'built' mean?",
        [
            "One-sentence vibes in the chat box.",
            "Assembled layers: input, context, reasoning, quality, output.",
        ],
        1,
    ),
    58: (
        "AI doesn't turn chaos into clarity. Who does?",
        [
            "The latest flagship model.",
            "You—by filtering, sequencing, scoping, and validating the problem.",
        ],
        1,
    ),
    59: (
        "It's not the model. It's the operator. What should you upgrade first?",
        [
            "Switch brands every week.",
            "Your prompt system: structure, constraints, and reuse.",
        ],
        1,
    ),
    60: (
        "AI for school & research (2026). What non-negotiable habit?",
        [
            "Trust fluent prose as citations.",
            "Verify sources; match tool to task (tutor vs search vs papers).",
        ],
        1,
    ),
    64: (
        "Your output is a recipe and you're missing ingredients. Those ingredients are:",
        [
            "More adjectives in the prompt.",
            "Layers: input, context, reasoning, quality, advanced control, output.",
        ],
        1,
    ),
    65: (
        "Data stack post: main idea?",
        [
            "One vendor owns the whole path from question to chart.",
            "Different tools for ask, store, model, visualize—wire the right stage.",
        ],
        1,
    ),
    70: (
        "Deck AI tools: what should you optimize for?",
        [
            "Picking the single 'best' app forever.",
            "Matching the job: speed vs Slides vs brand vs enterprise story.",
        ],
        1,
    ),
    74: (
        "Your AI output is layered—you just don't see it. Practical takeaway?",
        [
            "Treat it as one blob in, one blob out.",
            "Name and strengthen each layer so weak ones don't collapse the result.",
        ],
        1,
    ),
    75: (
        "Automate in layers—not one Zap to rule them all. Why?",
        [
            "Every workflow should be one mega-workflow.",
            "Simple glue vs logic-heavy flows vs AI steps need different tools.",
        ],
        1,
    ),
    84: (
        "AI doesn't fail—your control system does. What helps?",
        [
            "Skip validation; ship the first answer.",
            "Define intent, context, reasoning path, quality gate, then output.",
        ],
        1,
    ),
    89: (
        "Results feel random. The post blames your what?",
        [
            "API latency.",
            "Process: skipping structured steps between input and output.",
        ],
        1,
    ),
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    polls_path = root / "data" / "polls.json"
    data = json.loads(polls_path.read_text(encoding="utf-8"))
    n = 0
    for item in data.get("items", []):
        rid = item.get("related_post_id")
        if not isinstance(rid, int):
            continue
        if rid in ROLE_STACK_IDS:
            q, opts, cid = ROLE_STACK_POLL
        elif rid in TAILORED:
            q, opts, cid = TAILORED[rid]
        else:
            continue
        if item.get("question") == q and item.get("options") == opts and item.get("correct_option_id") == cid:
            continue
        item["question"] = q
        item["options"] = opts
        item["correct_option_id"] = cid
        n += 1
    polls_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {n} poll rows in {polls_path}")


if __name__ == "__main__":
    main()
