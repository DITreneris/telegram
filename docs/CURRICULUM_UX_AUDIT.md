# Curriculum UX audit (posts + quizzes)

**Scope:** [web/public/posts.json](../web/public/posts.json) and [data/polls.json](../data/polls.json) as consumed by the Telegram queue and web UI.  
**Last reviewed:** 2026-04-05  
**Counts (snapshot):** 98 posts, 98 polls (1:1 `related_post_id` coverage), post `id` range 1–123 with intentional numeric gaps (run `python scripts/audit_posts_png_quizzes.py` for live counts).

This document is a **qualitative + structural** review from learner UX, pedagogy, and social–emotional (SEL) angles. It does not replace [docs/EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md) (authoring mechanics) or [docs/QUEUE_SYNC.md](QUEUE_SYNC.md) (manifest build).

For a **long-form LLM-ready audit** (including **KISS–Marry–Kill** triage, a full **low hanging fruits** inventory, and extended weakest-units coverage), use [UX_CONVERSION_AUDIT_PROMPT.md](UX_CONVERSION_AUDIT_PROMPT.md).

**Full 98-post run (2026-04-05):** [CURRICULUM_UX_AUDIT_FULL_2026-04-05.md](CURRICULUM_UX_AUDIT_FULL_2026-04-05.md) — metrics-backed memo, TOP 10, LHF, KMK, wave map. **W1 content pass** applied the same day: `topic_key` **`framework_layers_canonical`** on **id 34**; qualitative wording on **4, 9, 27, 113, 114** (removed unsourced **90%/10%/1%**-style body claims where flagged); [data/content.json](../data/content.json) regenerated via `sync_queue_from_posts.py --in-place`. **W2 / W4 / stack trim (later pass):** **104–123** copy rhythm diversified; [data/post_journey_order.json](../data/post_journey_order.json) interleaves that band with other post types; role-stack rows shortened via a **Designer (32) reference stack** (see [CHANGELOG.md](../CHANGELOG.md) `[Unreleased]`).

---

## 1. How someone actually experiences the curriculum

- **Telegram path:** Many users receive **photo → caption text → poll** per logical “lesson,” then advance. Early in the queue, **the same headline theme repeats three times** with different copy (`option` 1 → 2 → 3 for the first ten themes). That is powerful for spaced variation *if* someone sees all three; for a fast click-through learner it reads as **near-duplicate messaging** and can feel like “the bot is stuck.”
- **Web/social path:** Single posts surface out of order. **Confrontational titles** (e.g. “Your AI isn’t underperforming. You are.”) work for scroll-stop **only if** the body immediately **reframes with support**; several bodies stay in accusatory “most people” mode longer than ideal for anxious readers.
- **ID gaps** (missing slots such as 40, 45, 50, …): harmless technically, but if humans ever map “lesson 55” to `id`, **gaps create support confusion** (“is my export broken?”). **Support note:** post `id` is the canonical slot in `posts.json`; gaps are intentional. Row count is **98 posts**, not “123 lessons.” Run `python scripts/audit_posts_png_quizzes.py` for live counts.

---

## 2. Audit criteria (rubric)

Use these when revising copy or approving new rows.

| Criterion | What “good” looks like | What to flag |
|-----------|------------------------|--------------|
| **Cognitive load** | One main idea + one memorable action; jargon defined in-line | Stacked frameworks (INPUT/CONTEXT/…) **without** a single “do this next” line |
| **Redundancy** | Intentional spaced repetition with **visible angle change** | Same bullets reordered; same metaphor (slot machine, toy, mirror) with minimal new information |
| **Pedagogical evidence** | Claims tied to observable behavior (“vague ask → generic output”) | **Unsourced statistics** (“90%,” “80% of users,” “under 1%”) presented as facts |
| **Quiz alignment** | Question forces **discrimination** between plausible choices; correct answer matches the *post’s* argument | Always-obvious distractors; correct answer always in the **same button position** |
| **SEL / tone** | Direct but not degrading; “you” used to invite agency | Shame-forward framing without a competence path; fear-of-replacement as the only motivator |
| **Style consistency** | One CTA pattern (`https://…` vs `→`); one voice per “series” | Mix of manifesto voice, LinkedIn-carousel voice, and tool-directory voice in one run |
| **Grammar / mechanics** | Punctuation supports scan-reading (especially on mobile) | Spacing around em dashes, inconsistent **bold** usage, very long URL lines without line breaks |
| **Brevity** | Every paragraph earns its place in a **short** vertical format | Repeated “Same AI. Different behavior.” closures; link + tagline repeated identically |

---

## 3. Structural findings

### 3.1 Planned redundancy (strength + risk)

- **Ten core `topic_key` themes × three variants** (`ai_mirror_inputs`, `please_vs_precision`, `guessing_vs_prompting`, etc.) across `id` 1–30: strong **deliberate repetition** of the same curriculum spine.
- **Risk:** In linear delivery, **30 items** can feel like one idea in ten echoes. **Mitigation ideas:** add a one-line **variant label** in copy (“Angle: constraints” / “Angle: templates”); or **interleave** non-core posts between variants (queue-level change, not only JSON).

### 3.2 Template fatigue: “How {role} uses AI: decisions & stack”

Posts such as **32, 37, 41, 46, 51, 71, 76, 81, 86, 93, 94, 95, 96, 97, 98, 99** share the same scaffold (hook → 🔹 blocks → one flow → bold punchline → question). Pedagogically clear; **UX-wise**, back-to-back consumption blurs **which role-specific insight** was unique.

**Improvement:** For each role, lead with **one non-generic constraint** (e.g. CMO: “one primary metric”; Finance: “model is not the ledger”) *in the first two lines*, and **shorten** the repeated “Thinking & … / Research …” pattern where tools are identical across posts.

### 3.3 Repeated “layer stack” framework

At least **eight** posts echo the same layered diagram (INPUT → CONTEXT → REASONING / QUALITY → OUTPUT), including **33, 34, 44, 54, 64, 74, 84, 89**. The idea is sound; the **duplication** competes with the “decisions & stack” series for the learner’s “this again?” budget.

**Improvement:** Merge to **one canonical “layers” post** + short **cross-links** in others (“See layers: post 34”) *or* differentiate each post by **one layer only** (deep dive on QUALITY vs CONTEXT).

### 3.4 `topic_key` (analytics + journey)

**Status (repo):** All **98** posts in [web/public/posts.json](../web/public/posts.json) now have a `topic_key` (backfill completed; see [CHANGELOG.md](../CHANGELOG.md) `[Unreleased]`). Use keys for grouping, journey tooling, and audits.

**Ongoing:** When adding new posts, assign a stable `topic_key` following existing patterns (`stack_*`, `framework_layers_*`, theme slug).

---

## 4. Quiz (poll) UX

- **Coverage:** Every post has a poll — excellent for **check-for-understanding**.
- **Position bias:** After rotation by post order ([scripts/rotate_poll_correct_options.py](../scripts/rotate_poll_correct_options.py)), the bank targets a **~50/50** split. **Snapshot (repo):** `correct_option_id` **0 → 49**, **1 → 49** (98 binary polls). **Re-check** after bulk edits: `python -c "import json;d=json.load(open('data/polls.json'));print(sum(1 for i in d['items'] if i.get('correct_option_id')==0), sum(1 for i in d['items'] if i.get('correct_option_id')==1))"`. Habitual learners may still **always tap the same button** without reading—rotation is the main lever (Telegram does not label “first/second”).
- **Difficulty:** Most items are **binary good/bad** pairs where the wrong line is visibly weak. Fine for onboarding; **weak for intermediate** users who need **near-miss** distractors.
- **Improvement:** Rotate correct index intentionally; add **one plausible wrong** option (three-option polls if product allows); occasional “which is *least* helpful?” to force slower reading.
- **Three-option polls:** Telegram and [schemas.py](../schemas.py) allow up to **10** options, but this bot’s manifest and UX are optimized for **binary** checks today. Near-miss distractors for intermediate learners are a **product decision** (copy + optional handler copy). See §4 note in changelog-backed passes.
- **2026 follow-up pass:** Role-stack polls no longer share one identical question stem; several items rephrased for **non-specialists** (less API/RAG/weights jargon). See [CHANGELOG.md](../CHANGELOG.md) `[Unreleased]` “Quiz bank”.

---

## 5. Weakest posts / clusters (priority list)

Below: **weakest from a learner + SEL lens**, with concrete improvement directions. IDs refer to [web/public/posts.json](../web/public/posts.json).

| Priority | IDs / cluster | Issue | Improvement possibilities |
|----------|----------------|-------|---------------------------|
| **P1** | **1–30** (especially **1, 2, 3** headlines) | Accusatory openers; repetition without a labeled “why another pass” | Soften first line while keeping punch; add **one-line progress marker** per variant; consider **one** supportive reframe (“This is fixable by…”) above the fold |
| **P1** | **101** | Presents **~80% / ~15% / &lt;1%** as facts; heavy emoji; weak epistemic hygiene | Replace invented splits with **qualitative tiers** (“many / some / few”) or cite a source; reduce emoji density for credibility |
| **P1** | **102** | Competitiveness + replacement anxiety as core motivator | Balance with **agency** (“what to learn this quarter”); avoid implying inevitability of job loss without nuance |
| **P2** | **34, 39, 44, 54, 64, 74, 84, 89** | Same framework repeated | Consolidate or differentiate one layer per post (see §3.3) |
| **P2** | **Role stack** series (see §3.2) | Indistinguishable shape across roles | Open with role-specific **failure mode**; trim duplicate tool lists; vary closing question |
| **P2** | **100** | Strong closer but **“115+ prompts”** is a product claim — must stay accurate or it erodes trust | Align copy with actual catalog; or soften to “full library on site” |
| **P3** | **31** | Tone shift (directory + TL;DR) vs manifesto series — fine alone, **jarring** if adjacent | Add a bridging sentence (“Practical pick: …”) or place after a **tooling** section header in journey |
| **P3** | **33** | Good concise variant of “guessing”; still overlaps **3, 13, 23** | Keep as the **canonical short** version; trim longer duplicates or point readers to the short one |
| **P3** | **103** | Strong metaphor; similar to **42, 38, 59** theme cluster (“operator / thinking / workflow”) | Merge metaphors across cluster or stagger with non-meta posts |

---

## 6. Style, grammar, and shortening opportunities

- **CTA consistency:** Mix of `→ promptanatomy.app`, `https://promptanatomy.app`, and `👉 Full system…` — pick **one pattern** per channel (Telegram vs web) and shorten where the image already shows the brand.
- **Punctuation:** Phrases like “Mostly — it doesn’t” (em dash with spaces) read fine on web; on narrow phones, **comma form** often scans faster.
- **Bold:** `**decisions + flow**` posts use bold for emphasis; manifesto posts mostly don’t — **series-level rule** helps brand cohesion.
- **Cut candidates:** Closing blocks that repeat **“Same AI. Different result.”** family; replace with **one** concrete micro-task (“Rewrite your last vague prompt using role + output shape”).

---

## 7. Recommended next steps (operational)

1. **Workshop pass:** Apply the rubric in §2 to **P1** rows first (tone + unsubstantiated stats + fear-only framing).
2. **Quiz pass:** Randomize `correct_option_id` and strengthen distractors ([data/polls.json](../data/polls.json)); re-run [scripts/sync_polls_to_web.mjs](../scripts/sync_polls_to_web.mjs) before web build if applicable.
3. **Metadata pass:** Backfill `topic_key` for rows missing it (helps [data/post_journey_order.json](../data/post_journey_order.json) and reporting).
4. **Queue design:** If Telegram fatigue shows up in ops feedback, adjust **interleaving** in [queue_manifest_sync.py](../queue_manifest_sync.py) / journey JSON rather than only rewriting copy.

---

## 8. Related docs

- [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md) — authoring and quiz semantics  
- [QUEUE_SYNC.md](QUEUE_SYNC.md) — how posts and polls become the manifest  
- [CONTENT_INVENTORY.md](CONTENT_INVENTORY.md) — coverage snapshot  
- [docs/golden_standard.md](golden_standard.md) — CI and content pipeline invariants  
