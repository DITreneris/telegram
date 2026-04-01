"""Patch data/polls.json: replace generic 11+ quiz template with per-post lesson questions.

Run from repo root: python scripts/apply_poll_lesson_patches.py
Keeps ids and theme_note; updates question, options, correct_option_id only.
"""

from __future__ import annotations

import json
from pathlib import Path

# related_post_id -> patch (correct answer is always option index 1 unless noted)
PATCHES: dict[int, dict[str, object]] = {
    11: {
        "question": "Outputs feel generic. What should you define so the model stops improvising blindly?",
        "options": [
            "Switch to a different frontier model.",
            "What the AI is, what it sees, what it must produce, and how good it must be.",
        ],
        "correct_option_id": 1,
    },
    12: {
        "question": "Why does chatty, polite wording often weaken operational results?",
        "options": [
            "Models are trained to ignore short prompts.",
            "Extra words that do not add structure add noise; constraints beat politeness.",
        ],
        "correct_option_id": 1,
    },
    13: {
        "question": "Your answers feel inconsistent. What is the most likely root cause?",
        "options": [
            "The provider keeps changing weights overnight.",
            "Your inputs are inconsistent: task, constraints, and output were never defined clearly.",
        ],
        "correct_option_id": 1,
    },
    14: {
        "question": "Outputs are long, safe, and hard to use. What fix matches strong prompting?",
        "options": [
            "Ask it to try harder and be more creative.",
            "Add constraints: length, structure, tone, and goal (e.g. 150 words, one actionable tip).",
        ],
        "correct_option_id": 1,
    },
    15: {
        "question": "You want stable quality across many tasks. What scales better?",
        "options": [
            "Reinvent wording from scratch every single time.",
            "Reuse templates: same structure and expectations, swap only the inputs.",
        ],
        "correct_option_id": 1,
    },
    16: {
        "question": "Slot-machine style use produces random answers. What creates real control?",
        "options": [
            "Write longer, friendlier paragraphs.",
            "Defined role, context, specific output, measurable constraints—then reuse that pattern.",
        ],
        "correct_option_id": 1,
    },
    17: {
        "question": "Results plateau. Where does the biggest jump usually come from?",
        "options": [
            "Trying another chatbot brand.",
            "One structured instruction—role, objective, constrained format—then reuse it.",
        ],
        "correct_option_id": 1,
    },
    18: {
        "question": "Version 1: broad ideas. Version 2: sharp, usable ideas. What actually changed?",
        "options": [
            "More creative adjectives.",
            "Structure: role, audience, goal, output shape (e.g. five hooks with angle), tone.",
        ],
        "correct_option_id": 1,
    },
    19: {
        "question": "Users chase better answers but little improves. What fixes the core issue?",
        "options": [
            "More retries with the same vague ask.",
            "Standardize logic: role, context, output, constraints—so results become predictable.",
        ],
        "correct_option_id": 1,
    },
    20: {
        "question": "Exploratory prompts are fun but do not scale. What shifts AI from toy to system?",
        "options": [
            "Ask more open-ended what-if questions.",
            "Execution mode: role, task, expected result, and quality bar—each time.",
        ],
        "correct_option_id": 1,
    },
    21: {
        "question": "Weak answers feel like the model failed. What is the post arguing?",
        "options": [
            "You need fine-tuning or a custom GPT.",
            "AI mirrors your prompt: vague request tends to produce safe, average completions.",
        ],
        "correct_option_id": 1,
    },
    22: {
        "question": "Replace polite human-style requests with what?",
        "options": [
            "Longer explanations of context and feelings.",
            "Role, context, output, and constraints so the model has direction.",
        ],
        "correct_option_id": 1,
    },
    23: {
        "question": "Trial-and-error without a system is closest to:",
        "options": [
            "Structured professional prompting.",
            "Guessing in front of a very capable autocomplete.",
        ],
        "correct_option_id": 1,
    },
    24: {
        "question": "Commands like “make it better” fail because:",
        "options": [
            "The model is lazy by design.",
            "The model completes instructions; with no concrete success criteria you get safe guesses.",
        ],
        "correct_option_id": 1,
    },
    25: {
        "question": "If every task starts from a blank prompt, what happens to leverage?",
        "options": [
            "You maximize creative surprise.",
            "Nothing compounds: work stays slow and results stay inconsistent.",
        ],
        "correct_option_id": 1,
    },
    26: {
        "question": "You blame the model for inconsistency. Often the real issue is:",
        "options": [
            "Silent model updates.",
            "Your process: inputs and expectations change every time.",
        ],
        "correct_option_id": 1,
    },
    27: {
        "question": "Powerful models used at low capacity usually means:",
        "options": [
            "You are on the wrong subscription tier.",
            "You only start a conversation instead of specifying exactly what to do.",
        ],
        "correct_option_id": 1,
    },
    28: {
        "question": "Before: “Help me improve this text.” After: role, goal, audience, constraints. The gap is:",
        "options": [
            "Friendlier tone.",
            "Structure and explicit acceptance criteria—not casual wording tweaks.",
        ],
        "correct_option_id": 1,
    },
    29: {
        "question": "Iteration without a stable structure tends to:",
        "options": [
            "Converge quickly every time.",
            "Stay chaotic: each attempt still starts from zero.",
        ],
        "correct_option_id": 1,
    },
    30: {
        "question": "Phase 1 is play and explore. For dependable work you need:",
        "options": [
            "More playful prompts.",
            "Defined role, context, specific output, constraints—execution, not chat.",
        ],
        "correct_option_id": 1,
    },
    31: {
        "question": "Weak outputs often come from vague asks. What is the best next step?",
        "options": [
            "Collect more image-generation apps.",
            "Name role, audience, output shape, and constraints—turn the chat into a brief.",
        ],
        "correct_option_id": 1,
    },
    32: {
        "question": "A stacked prompt should separate layers instead of one blob. Which set fits?",
        "options": [
            "Only the final question—no context.",
            "Input, context, reasoning steps, and quality gates.",
        ],
        "correct_option_id": 1,
    },
    33: {
        "question": "ICQRA-style framing pushes you away from one vague sentence toward:",
        "options": [
            "Shorter chats with no structure.",
            "Layered brief: instruction, context, query, rules/rubric, and assessment-style checks.",
        ],
        "correct_option_id": 1,
    },
    34: {
        "question": "Models comply with what you specify—they do not read your mind. So you should:",
        "options": [
            "Rely on implied goals and shared culture.",
            "Design explicit instructions and constraints up front.",
        ],
        "correct_option_id": 1,
    },
    36: {
        "question": "For a content creator, what matters as much as the tool stack?",
        "options": [
            "Posting on every platform daily.",
            "Clear decisions in the prompt: audience, deliverable, and constraints.",
        ],
        "correct_option_id": 1,
    },
    37: {
        "question": "You need a caption. Which ask is closer to professional prompting?",
        "options": [
            "Write something catchy.",
            "State role plus exact deliverable (e.g. one hook under 220 characters, audience X).",
        ],
        "correct_option_id": 1,
    },
    38: {
        "question": "Repeated weekly work. What beats one-off creative vibes?",
        "options": [
            "A brand-new random prompt every time.",
            "Reusable templates: stable structure, parameterized inputs.",
        ],
        "correct_option_id": 1,
    },
    39: {
        "question": "Shipping on a cadence requires:",
        "options": [
            "Waiting for inspiration.",
            "A repeatable prompt system—not only one-off prompts.",
        ],
        "correct_option_id": 1,
    },
    41: {
        "question": "Sharper first drafts start when you:",
        "options": [
            "Ask for “high quality” and “professional.”",
            "Define explicit success criteria before generation.",
        ],
        "correct_option_id": 1,
    },
    42: {
        "question": "Serious work usually rewards:",
        "options": [
            "Wildcard creative prompts.",
            "Boring, explicit specs—role, constraints, format—over personality flourishes.",
        ],
        "correct_option_id": 1,
    },
    43: {
        "question": "The model keeps missing the brief. First lever to pull?",
        "options": [
            "Switch models immediately.",
            "Tighten constraints and restate the spec—not model-hopping.",
        ],
        "correct_option_id": 1,
    },
    44: {
        "question": "Multi-part asks turn mushy. Better mental model?",
        "options": [
            "One giant paragraph with everything mixed together.",
            "Layer the ask like a burger—distinct layers, not soup.",
        ],
        "correct_option_id": 1,
    },
    46: {
        "question": "You want outline, full doc, and slides in one shot. Safer approach?",
        "options": [
            "One mega-prompt that does all three.",
            "One clear job per prompt; split multi-part work into steps.",
        ],
        "correct_option_id": 1,
    },
    47: {
        "question": "You need JSON or a strict format. What helps most?",
        "options": [
            "Say “follow the format carefully.”",
            "Include an example of the exact shape you want.",
        ],
        "correct_option_id": 1,
    },
    48: {
        "question": "Before generating, specify:",
        "options": [
            "Only the general topic.",
            "What “done” looks like: structure, length, and must-include elements.",
        ],
        "correct_option_id": 1,
    },
    49: {
        "question": "Risky or sensitive tasks need:",
        "options": [
            "Casual tone so the model relaxes.",
            "Red-team style constraints: forbidden paths, required checks, explicit safety bounds.",
        ],
        "correct_option_id": 1,
    },
    51: {
        "question": "A long report in one shot often fails. Better workflow?",
        "options": [
            "Regenerate until it fits.",
            "Outline first, then expand section by section using the outline as anchor.",
        ],
        "correct_option_id": 1,
    },
    52: {
        "question": "Micro-copy (subjects, titles) usually needs:",
        "options": [
            "Long personality-driven stories.",
            "Precision: tight limits on length and intent over flair.",
        ],
        "correct_option_id": 1,
    },
    53: {
        "question": "The model sounds confident but might be wrong. You should:",
        "options": [
            "Treat fluent prose as fact.",
            "Separate fluency from correctness—verify and add check steps in the workflow.",
        ],
        "correct_option_id": 1,
    },
    54: {
        "question": "A prompt that worked well should be:",
        "options": [
            "Deleted so you stay creative.",
            "Saved and reused like a code snippet, with parameters swapped.",
        ],
        "correct_option_id": 1,
    },
    56: {
        "question": "Judging AI output fairly means:",
        "options": [
            "Going with your gut.",
            "Scoring against an explicit rubric you stated (or implied) up front.",
        ],
        "correct_option_id": 1,
    },
    58: {
        "question": "You are stuck after a bad answer. Best retry pattern?",
        "options": [
            "Immediately switch models.",
            "Restate role and constraints, then retry with the same model.",
        ],
        "correct_option_id": 1,
    },
    59: {
        "question": "You want several variants. Prefer to vary:",
        "options": [
            "Only the model name.",
            "Constraints and angles while holding the task steady.",
        ],
        "correct_option_id": 1,
    },
    60: {
        "question": "Long-term leverage usually comes from:",
        "options": [
            "Starting from zero every Monday.",
            "A library of proven prompts tuned to your role.",
        ],
        "correct_option_id": 1,
    },
    62: {
        "question": "Brand-safe tone should live where?",
        "options": [
            "Implied from company culture.",
            "In the written spec: tone rules, words to avoid, and safety constraints.",
        ],
        "correct_option_id": 1,
    },
    64: {
        "question": "Turn chats into playbooks by:",
        "options": [
            "Deleting threads after each task.",
            "Structured debriefs: what worked, constraints used, reusable template.",
        ],
        "correct_option_id": 1,
    },
    65: {
        "question": "When quality is weak, many people blame the tool. Usually fix first:",
        "options": [
            "Buy another subscription.",
            "Prompt design: a clearer brief beats another tool.",
        ],
        "correct_option_id": 1,
    },
    70: {
        "question": "Pick tools after you know:",
        "options": [
            "Every feature on the market.",
            "The job-to-be-done and the outputs you need.",
        ],
        "correct_option_id": 1,
    },
    71: {
        "question": "Healthy skepticism toward AI outputs means:",
        "options": [
            "Avoiding AI entirely.",
            "Treating prompts and responses like experiments you measure.",
        ],
        "correct_option_id": 1,
    },
    74: {
        "question": "Slide outline versus narrative body. What sequence works better?",
        "options": [
            "One prompt that mixes both with no spine.",
            "Structure first (outline), then narrative expansion anchored to that spine.",
        ],
        "correct_option_id": 1,
    },
    75: {
        "question": "Operations rhythm improves when you:",
        "options": [
            "Chase the newest model weekly.",
            "Keep the stack stable and make prompts clearer and repeatable.",
        ],
        "correct_option_id": 1,
    },
    76: {
        "question": "You should not outsource final judgment. Prompt for:",
        "options": [
            "One definitive answer you will never check.",
            "Options and tradeoffs—you decide.",
        ],
        "correct_option_id": 1,
    },
    81: {
        "question": "To keep code and AI-assisted work aligned, what should stay synchronized?",
        "options": [
            "Only product copy—tests and prompts can diverge.",
            "Specs, tests, and prompt acceptance criteria.",
        ],
        "correct_option_id": 1,
    },
    84: {
        "question": "Builders ship when prompts encode:",
        "options": [
            "Vibes and enthusiasm.",
            "Acceptance checks: what must be true for the output to count as done.",
        ],
        "correct_option_id": 1,
    },
    86: {
        "question": "Specialists get stronger results with:",
        "options": [
            "Broad “do everything” requests.",
            "Narrow, testable asks with clear pass or fail.",
        ],
        "correct_option_id": 1,
    },
    89: {
        "question": "Review AI output like a PM. Focus on:",
        "options": [
            "Whether it sounds smart.",
            "Scope, acceptance criteria, and risks.",
        ],
        "correct_option_id": 1,
    },
    93: {
        "question": "Late-stage polish usually means:",
        "options": [
            "Adding more adjectives.",
            "Shorten, sharpen, and add proof—tighten to the spec.",
        ],
        "correct_option_id": 1,
    },
    94: {
        "question": "CTAs in copy get watered down because:",
        "options": [
            "Models default to bold CTAs.",
            "Models hedge—make the CTA explicit in the prompt.",
        ],
        "correct_option_id": 1,
    },
    95: {
        "question": "One message speaks to execs, interns, and customers at once. Fix?",
        "options": [
            "One clever universal line.",
            "Split into separate prompts—one audience per message.",
        ],
        "correct_option_id": 1,
    },
    96: {
        "question": "Numbers and dates in drafts blur unless you:",
        "options": [
            "Hope the model remembers the brief.",
            "Ask explicitly for formats, ranges, and units in the prompt.",
        ],
        "correct_option_id": 1,
    },
    97: {
        "question": "Lists without rules tend to sprawl. Better:",
        "options": [
            "Ask for “a few” bullets.",
            "Cap count, define order (e.g. priority), and required versus optional items.",
        ],
        "correct_option_id": 1,
    },
    98: {
        "question": "Flat stories usually lack:",
        "options": [
            "More emojis.",
            "Arc in the brief: hook, tension, payoff.",
        ],
        "correct_option_id": 1,
    },
    99: {
        "question": "Content that never drives a next step often failed because:",
        "options": [
            "Readers love ambiguity.",
            "The prompt omitted the next step or CTA—close the loop explicitly.",
        ],
        "correct_option_id": 1,
    },
    100: {
        "question": "Even a “short stack” prompt still needs:",
        "options": [
            "Only a topic keyword.",
            "Role, audience, output shape, and constraints—in compact form.",
        ],
        "correct_option_id": 1,
    },
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "data" / "polls.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    seen: set[int] = set()
    for item in data["items"]:
        rid = item.get("related_post_id")
        if not isinstance(rid, int):
            continue
        patch = PATCHES.get(rid)
        if not patch:
            continue
        item["question"] = patch["question"]
        item["options"] = patch["options"]
        item["correct_option_id"] = patch["correct_option_id"]
        seen.add(rid)
    missing = set(PATCHES.keys()) - seen
    if missing:
        raise SystemExit(f"No poll rows for related_post_id: {sorted(missing)}")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {len(seen)} poll rows in {path}")


if __name__ == "__main__":
    main()
