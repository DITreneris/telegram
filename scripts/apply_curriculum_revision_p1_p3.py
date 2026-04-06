#!/usr/bin/env python3
"""One-off curriculum edits for P1–P3 (posts.json). Run from repo root."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POSTS = REPO / "web" / "public" / "posts.json"

FIX_CTA = (
    "\n\nThis is fixable: name role, audience, output shape, and constraints on your next prompt.\n\n"
    "https://promptanatomy.app"
)

# Pass label + angle + softened openers for spine ids 1–30 (by post id)
SPINE_PREFIX: dict[int, str] = {
    1: "Pass 1 — Angle: your output mirrors the quality of your spec.\n\n💥 Blunt headline, fair point: generic answers usually mean the ask was generic—not that the model is \"broken.\"\n\n",
    2: "Pass 1 — Angle: clarity beats conversational fluff.\n\n🙅 You don't need to be rude. You do need to be explicit—soft asks often become soft answers.\n\n",
    3: "Pass 1 — Angle: hope is not a prompting strategy.\n\n🎲 Vague asks force the model to guess. Guessing feels random because it is.\n\n",
    4: "Pass 1 — Angle: define \"good\" before you ask.\n\n🎯 If you never specify format, tone, or success, the model defaults to safe average.\n\n",
    5: "Pass 1 — Angle: reuse beats reinventing every time.\n\n🌀 New prompt every task → new variability every time.\n\n",
    6: "Pass 1 — Angle: configuration beats conversation.\n\n🎛️ \"Ask and hope\" adds friction; defined role + output + constraints removes it.\n\n",
    7: "Pass 1 — Angle: one structured prompt beats ten vague tries.\n\n🚀 Model-hopping rarely fixes a missing spec.\n\n",
    8: "Pass 1 — Angle: structure is the lever, not adjectives.\n\n⚖️ Same task, same model—different spec → different usefulness.\n\n",
    9: "Pass 1 — Angle: prompting is design, not typing speed.\n\n📊 Many people skip success criteria; the model then picks \"fine enough.\"\n\n",
    10: "Pass 1 — Angle: systems beat endless play.\n\n🧸 Exploration is fine; repeatable work needs repeatable prompts.\n\n",
    11: "Pass 2 — Angle: inputs, not \"bad AI.\"\n\n🪞 Weak outputs usually mean the brief was thin—fix the spec first.\n\n",
    12: "Pass 2 — Angle: operational noise in the prompt.\n\n✂️ Chatty filler often dilutes the actual task.\n\n",
    13: "Pass 2 — Angle: inconsistent inputs → inconsistent outputs.\n\n🎯 If the task shape changes every time, so will the answer.\n\n",
    14: "Pass 2 — Angle: constraints create usable length and edge.\n\n🧱 No length, tone, or goal → long safe mush.\n\n",
    15: "Pass 2 — Angle: templates compound; one-offs don't.\n\n🔁 Standardize structure so quality stabilizes across tasks.\n\n",
    16: "Pass 2 — Angle: slot-machine use doesn't scale.\n\n🎰 Pulling the lever without a spec is still gambling.\n\n",
    17: "Pass 2 — Angle: instruction quality plateaus before model quality.\n\n🔭 One tight prompt often beats many loose ones.\n\n",
    18: "Pass 2 — Angle: A/B the spec, not the adjectives.\n\n🧪 Same model—structure is what changed Version 2.\n\n",
    19: "Pass 2 — Angle: stop chasing answers; fix the input system.\n\n🎢 Retries without structure stay noisy.\n\n",
    20: "Pass 2 — Angle: execution mode for real work.\n\n🎡 Fun exploration ≠ dependable delivery.\n\n",
    21: "Pass 3 — Angle: the mirror metaphor (agency, not shame).\n\n🪞 \"Meh\" output often started as a vague prompt—you can change that next message.\n\n",
    22: "Pass 3 — Angle: personification weakens instructions.\n\n🎭 Requests beat specs by default; swap to role + task + constraints.\n\n",
    23: "Pass 3 — Angle: smart autocomplete still needs a spec.\n\n🧩 Without a system, you're iterating in the dark.\n\n",
    24: "Pass 3 — Angle: \"make it better\" isn't a spec.\n\n🌫️ Concrete success criteria beat vibe requests.\n\n",
    25: "Pass 3 — Angle: compound with reuse.\n\n🔀 One-offs never get a feedback loop.\n\n",
    26: "Pass 3 — Angle: blame the process before the model.\n\n🎚️ Changing inputs every time guarantees changing outputs.\n\n",
    27: "Pass 3 — Angle: low capacity = underspecified asks.\n\n💡 The model already has headroom; the prompt isn't using it.\n\n",
    28: "Pass 3 — Angle: acceptance criteria vs small talk.\n\n✍️ Before/after differs by structure, not politeness.\n\n",
    29: "Pass 3 — Angle: iteration needs a scaffold.\n\n🔁 Tweaking without a template stays chaotic.\n\n",
    30: "Pass 3 — Angle: Phase 2 is dependable structure.\n\n🎮 Play is step one; systems are step two.\n\n",
}

# Strip old first block through first double newline after hook — we replace whole start
# Instead: for each id, replace content by finding first \n\n after emoji header... Too fragile.

# Simpler: for spine posts, replace known opening patterns (old) with prefix only where we match


def _strip_spine_header(content: str, post_id: int) -> str:
    """Remove original harsh/short opening through 'Hard truth' or similar so PREFIX can replace."""
    lines = content.split("\n")
    # Find first blank line after line 0-3 typical
    if post_id in (1,):
        # remove through "Hard truth—but necessary.\n\n"
        marker = "Hard truth—but necessary.\n\n"
        if marker in content:
            return content.split(marker, 1)[1]
    if post_id in (2,):
        m = "It's not making you more effective.\nIt's making your outputs worse.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (3,):
        m = "You're guessing.\n\nAnd your results prove it.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (4,):
        m = "You don't define the output.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (5,):
        m = "So are your results.\n\nAnd no, it's not the model.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (6,):
        m = "That's the whole game.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (7,):
        m = "One prompt.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (8,):
        m = "Completely different results.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (9,):
        m = "They think prompting = typing.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (10,):
        m = "That's when everything changed.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (11,):
        m = "Your inputs are.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (12,):
        m = "Operationally.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (13,):
        m = "You're throwing ideas at it.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (14,):
        m = "Here's why.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (15,):
        m = "look at your prompts.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (16,):
        m = "See what comes out.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (17,):
        m = "That's why most results plateau.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (18,):
        m = "run this test.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (19,):
        m = "instead of fixing their inputs.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (20,):
        m = "That's where most people hit the wall.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (21,):
        m = "It's mirroring you.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (22,):
        m = "It's efficient.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (23,):
        m = "They're not.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (24,):
        m = "It's vagueness.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (25,):
        m = "It's a system problem.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (26,):
        m = "That's what people say.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (27,):
        m = "They require better prompts.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (28,):
        m = "Two different approaches.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (29,):
        m = "instead of structure.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    if post_id in (30,):
        m = "They play with it.\n\n"
        if m in content:
            return content.split(m, 1)[1]
    raise ValueError(f"Could not strip header for post {post_id}")


def _replace_cta(content: str) -> str:
    for old in ("\n\n→ promptanatomy.app", "\n→ promptanatomy.app"):
        if old in content:
            return content.replace(old, FIX_CTA, 1)
    if content.rstrip().endswith("https://promptanatomy.app"):
        return content
    raise ValueError("No CTA found to replace")


def revise_spine_post(post: dict) -> dict:
    pid = post["id"]
    body = _strip_spine_header(post["content"], pid)
    post["content"] = SPINE_PREFIX[pid] + body
    post["content"] = _replace_cta(post["content"])
    return post


def main() -> None:
    data = json.loads(POSTS.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in data}

    for pid in range(1, 31):
        by_id[pid] = revise_spine_post(by_id[pid])

    # 101 — qualitative tiers, fewer emojis
    by_id[101]["content"] = (
        "The 3 types of AI users (illustrative—not a scientific census):\n\n"
        "1) Skeptics: tried once, did not build a habit.\n"
        "2) Casuals: occasional use like a quick search.\n"
        "3) Power users: pay where it helps, iterate, and use structure (role, context, constraints, format, success criteria).\n\n"
        "Most prompts stay vague: \"Make it better.\" Pros define the job so the model can execute.\n\n"
        "Same AI. Different outcome when the spec is different.\n\n"
        "AI rewards clear structure more than raw access.\n\n"
        "https://promptanatomy.app"
    )

    # 102 — SEL balance + agency
    by_id[102]["content"] = (
        "Most people won't be replaced by AI overnight.\n\n"
        "They can be outpaced by people who pair AI with judgment: clear specs, verification, and domain taste.\n\n"
        "A cheap subscription doesn't replace you—**how** you use the tool changes what you ship.\n\n"
        "Markets reward:\n"
        "— faster cycles when quality holds\n"
        "— lower cost per unit of good work\n"
        "— reliability, not just raw speed\n\n"
        "That's already visible across marketing, support, analysis, content, and ops.\n\n"
        "The mistake is assuming the model must beat you head-to-head. Often it only has to be \"good enough\" at the wrong stage of the workflow.\n\n"
        "**Agency:** pick one skill to compound—spec writing, critique, verification, or storytelling—and use AI to rehearse and accelerate that, not to skip thinking.\n\n"
        "Reflect: what part of your work still needs your judgment even when the draft is free?\n\n"
        "https://promptanatomy.app"
    )

    # 100 — soften product claim
    by_id[100]["content"] = by_id[100]["content"].replace(
        "👉 Full system (115+ prompts):\nhttps://promptanatomy.app",
        "Full prompt library and patterns on the site:\nhttps://promptanatomy.app",
    )

    # 31 — bridge + Summary label
    by_id[31]["content"] = (
        "Practical pick: match the image model to the job—not to hype.\n\n"
        "🖼️ Wrong image AI? Usually a random pick—not \"bad\" tools.\n\n"
        "By job:\n"
        "OpenAI / ChatGPT — https://chatgpt.com · accuracy, edits\n"
        "Midjourney — https://www.midjourney.com · look & mood\n"
        "Firefly — https://www.adobe.com/products/firefly.html · Adobe workflows\n"
        "Gemini — https://gemini.google.com · Google stack\n"
        "FLUX — https://blackforestlabs.ai · control, APIs\n"
        "Ideogram — https://ideogram.ai · text inside images\n\n"
        "Summary: accuracy→OpenAI · beauty→MJ · workflow→Firefly · Google→ease · control→FLUX · type→Ideogram\n\n"
        "Best for what—not \"best overall\"? Which do you use?\n"
        "https://promptanatomy.app"
    )

    # 33 — canonical short + pointer (differentiate from 3,13,23)
    by_id[33]["content"] = (
        "Short version of the \"guessing\" lesson (full passes in earlier cards on the same headline).\n\n"
        "You're not prompting—you're hoping the model fills in a blank you never named.\n\n"
        "If you would not brief a human with only \"help me with this,\" do not brief AI that way either; it mirrors the gap.\n\n"
        "They type: \"Give me ideas…\" \"Write something…\" \"Help me…\" Sometimes it works; often it doesn't, because there is no structure.\n\n"
        "Stack to aim for: INPUT → CONTEXT → REASONING → ADVANCED → QUALITY (how you check the answer).\n\n"
        "No structure → noisy outputs. Structure → repeatable results.\n\n"
        "Next step: rewrite your last vague ask with role + task + output shape + one constraint.\n\n"
        "https://promptanatomy.app"
    )

    # 103 — tie to adjacent \"operator\" cluster without merging posts
    by_id[103]["content"] = (
        "Most teams do not have an AI problem.\n\n"
        "They have a workflow problem—and that rhymes with the \"operator / thinking\" cards: better models don't fix vague prompts or missing handoffs.\n\n"
        "Models keep improving. Habits often don't.\n\n"
        "So teams buy frontier access, then run it with mushy asks and no process—like bolting a faster engine onto a car with loose wheels.\n\n"
        "A smarter model will not save a weak operator.\n\n"
        "The edge is moving from \"who has AI\" to \"who can run it with clear specs and review.\"\n\n"
        "In 2026, operator quality usually matters more than which logo is on the API—until the operator levels up, the model is idle horsepower.\n\n"
        "https://promptanatomy.app"
    )

    # P2: layer stack — 34 canonical; others shorten + point
    by_id[34]["content"] = (
        "Canonical \"layers\" card—other posts riff on one slice of this.\n\n"
        "AI is not a tool.\n\n"
        "It's a system.\n\n"
        "Most people treat AI like a chatbot: ask → answer → repeat. Behind every output is a stack:\n\n"
        "INPUT → what enters\n"
        "CONTEXT → what frames it\n"
        "REASONING → how logic is applied\n"
        "ADVANCED → constraints, tools, control\n"
        "QUALITY → evaluation and correction\n"
        "OUTPUT → final result\n\n"
        "Ignore the stack → results feel random. Control it → results get repeatable.\n\n"
        "https://promptanatomy.app"
    )
    by_id[39]["content"] = (
        "Layer focus: ROLE / TASK / CONTEXT / CONSTRAINTS / FORMAT / EVAL (plus memory, RAG, tools when relevant).\n\n"
        "Most AI users are stuck in unstructured asks → inconsistent outputs. "
        "See the full layer map in the \"AI is not a tool. It's a system.\" card.\n\n"
        "Unstructured → inconsistent → unreliable.\n\n"
        "They write: \"I need something…\" \"Make it better…\" with no context or constraints.\n\n"
        "Controlled setup names who the AI is, what it must do, what it needs, what it must not do, how to format, and how you'll check it.\n\n"
        "That's system design, not casual chat.\n\n"
        "Micro-task: add CONSTRAINTS and FORMAT lines to your next prompt.\n\n"
        "https://promptanatomy.app"
    )
    by_id[44]["content"] = (
        "Layer focus: INPUT / CONTEXT / REASONING / QUALITY / ADVANCED / OUTPUT—miss one and the \"burger\" falls apart.\n\n"
        "Your prompts fail when structure is missing, not because you lack adjectives.\n\n"
        "See the canonical layer list in the \"AI is not a tool. It's a system.\" post.\n\n"
        "Random input → hope → retry → frustration becomes predictable when you name each layer for your use case.\n\n"
        "https://promptanatomy.app"
    )
    by_id[54]["content"] = (
        "Layer focus: assembly beats typing—INPUT, CONTEXT+REASONING, QUALITY, ADVANCED, OUTPUT.\n\n"
        "Good prompts are built, not scribbled. Full diagram lives in the system/layers card.\n\n"
        "No structure → inconsistent results. Structured prompt → repeatable performance.\n\n"
        "https://promptanatomy.app"
    )
    by_id[64]["content"] = (
        "Layer focus: ingredients map to INPUT, CONTEXT, REASONING, QUALITY, ADVANCED, OUTPUT.\n\n"
        "Incomplete input → weak output; the model executes what you give it. Canonical layer names: see \"AI is not a tool. It's a system.\"\n\n"
        "https://promptanatomy.app"
    )
    by_id[74]["content"] = (
        "Layer focus: visibility—INPUT, CONTEXT, REASONING, QUALITY, ADVANCED, OUTPUT.\n\n"
        "Your AI output is layered even when you don't see it; weak layers collapse the rest. Full stack defined in the canonical system card.\n\n"
        "https://promptanatomy.app"
    )
    by_id[84]["content"] = (
        "Layer focus: control system under the hood—INPUT, CONTEXT, REASONING, core execution, ADVANCED (tools/memory), QUALITY gate, OUTPUT.\n\n"
        "Surface prompting alone skips the control system. See baseline layer map in \"AI is not a tool. It's a system.\"\n\n"
        "https://promptanatomy.app"
    )
    by_id[89]["content"] = (
        "Layer focus: process steps—clear INPUT, CONTEXT, structured reasoning, QUALITY check, OUTPUT.\n\n"
        "Skipping steps reads as \"random AI.\" The full layer vocabulary is in the canonical system card.\n\n"
        "https://promptanatomy.app"
    )

    # Role stacks: stronger first-line failure mode (already unique; tighten openings)
    role_tweaks = {
        32: "Designer failure mode: pretty pixels with a mushy brief—decisions before tools.\n\n",
        37: "Creator failure mode: volume without an audience decision—cadence dies first.\n\n",
        41: "CEO failure mode: reinventing the Tuesday brief—clarity and comms stack beats another assistant app.\n\n",
        46: "PM failure mode: roadmap theater without a \"done\" definition—prioritization before brainstorm bots.\n\n",
        51: "Support failure mode: friendly AI, unresolved tickets—resolution and policy ground truth first.\n\n",
        71: "CMO failure mode: creative churn without ICP or one primary metric—allocation before more AI concepts.\n\n",
        76: "Ops failure mode: Zaps everywhere, no source of truth—visibility before automation.\n\n",
        81: "Engineer failure mode: green CI, wrong product—spec → code → verify beats vibe commits.\n\n",
        86: "CTO failure mode: pilot folders that never ship—risk, architecture, velocity in one repeatable loop.\n\n",
        93: "Sales failure mode: more sequences, empty CRM truth—signal and coaching before spray-and-pray.\n\n",
        94: "HR failure mode: faster screens, no rubric—fair process and human gates before scaled noise.\n\n",
        95: "Finance failure mode: confident paragraphs, no audit trail—controls and Excel truth before narrative.\n\n",
        96: "EA failure mode: inbox zero, wrong priorities—time and coordination before raw speed.\n\n",
        97: "MLE failure mode: pretty curves no one reproduces—experiments, evals, shipping.\n\n",
        98: "E-com failure mode: traffic without margin—merch, campaigns, unit economics on one north star.\n\n",
        99: "Founder failure mode: ten tabs, fuzzy ICP—clarity under constraint before the stack debate.\n\n",
    }
    for rid, prefix in role_tweaks.items():
        c = by_id[rid]["content"]
        if not c.startswith(prefix):
            # insert after first paragraph (first \n\n)
            idx = c.find("\n\n")
            if idx == -1:
                by_id[rid]["content"] = prefix + c
            else:
                by_id[rid]["content"] = c[: idx + 2] + prefix + c[idx + 2 :]

    # topic_key backfill for posts missing it
    TOPIC_KEYS: dict[int, str] = {
        31: "image_tools_by_job",
        32: "stack_designer",
        33: "guessing_vs_prompting_short",
        36: "agreement_challenge_prompts",
        37: "stack_content_creator",
        38: "thinking_front_load",
        39: "stuck_unstructured_layers",
        41: "stack_ceo",
        42: "brain_use_vs_avoidance",
        43: "feeding_vs_directing",
        44: "prompt_burger_layers",
        46: "stack_product_manager",
        47: "pressure_not_politeness",
        48: "ai_reveals_level",
        49: "ai_follows_direction",
        51: "stack_customer_support",
        52: "polite_vs_precise_again",
        53: "patterns_not_personality",
        54: "prompts_built_not_written",
        56: "stack_social_media_manager",
        58: "chaos_to_clarity_you",
        59: "operator_not_model",
        60: "stack_education_research",
        62: "data_to_decisions_system",
        64: "recipe_layers",
        65: "stack_data_analysis",
        70: "stack_presentations",
        71: "stack_cmo",
        74: "layers_visibility",
        75: "stack_automation_agents",
        76: "stack_operations",
        81: "stack_software_engineer",
        84: "control_system_underneath",
        86: "stack_cto",
        89: "process_not_random",
        93: "stack_sales",
        94: "stack_hr",
        95: "stack_finance",
        96: "stack_executive_assistant",
        97: "stack_ml_engineer",
        98: "stack_ecommerce",
        99: "stack_founder",
        100: "thinking_problem_not_ai",
    }
    for pid, key in TOPIC_KEYS.items():
        by_id[pid]["topic_key"] = key

    ordered = [by_id[p["id"]] for p in data]
    POSTS.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", POSTS)


if __name__ == "__main__":
    main()
