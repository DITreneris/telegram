# Full curriculum UX + conversion audit (98 posts)

**Scope:** All rows in [web/public/posts.json](../web/public/posts.json) and matching items in [data/polls.json](../data/polls.json) (98 posts, 98 polls).  
**Method:** Repo-grounded analysis (inventory scripts, heuristic semantics audit, structured rubric from [CURRICULUM_UX_AUDIT.md](CURRICULUM_UX_AUDIT.md) and [UX_CONVERSION_AUDIT_PROMPT.md](UX_CONVERSION_AUDIT_PROMPT.md)).  
**Date:** 2026-04-05  

---

## 1. Executive summary

**Three largest problems**

1. **Template fatigue in two long bands:** (a) core spine **id 1–30** repeats each headline three times (`option` 1/2/3) with strong “Pass / Angle” labels—good for spaced learning, but Telegram-linear readers can still feel “stuck”; (b) **104–123** share one rhythmic scaffold (`—` separators, `👉` pointers); (c) **21× `stack_*`** role posts share one shape. Cognitive distinctiveness drops when many units arrive back-to-back.
2. **Unsourced quant claims in otherwise strong copy:** Explicit **90% / 10% / 1%** or **“top 10%”** / **“20% capacity”** lines read as census data and erode trust (same class of issue already fixed on **101**). **PNG headlines** still carry “90%” where the image is the source of truth—**body** copy should stay epistemically clean.
3. **Quiz–post overlap is often low** for template polls (`audit_post_quiz_semantics.py` Jaccard &lt; 0.08 for many ids)—not always wrong, but it flags **manual review** for “does this question force the lesson?”

**Where learners drop off**

- **Telegram:** After **photo + caption**, if the next item feels like a repeat (same `theme`, different pass), impatient users skip or mash **Next** without internalizing the angle label.
- **Web/social:** **104–123** scan well for 3s scroll-stop; **mid-body** can feel samey—drop-off is **boredom / pattern match**, not confusion.

**Clarity score: 78 / 100**

Strong structure (Pass/Angle, canonical **34**, clear CTAs, full PNG/poll coverage). Deductions: quant hygiene in a few bodies, serial homogeneity (dash series + stacks), and residual **poll–lesson** distance on early template quizzes.

---

## 2. User journey analysis

| Phase | Web / social | Telegram queue |
|--------|----------------|------------------|
| **0–3s** | `theme` + image = clear hook; confrontational lines still stop scroll if body reframes quickly. | Photo + first lines of caption; **Pass N** line orients if read. |
| **~5s scan** | Bullets / emojis / `—` blocks aid scan; stack posts dense with links—power users win, novices may skim tools only. | Same as caption scan; long stack lists can feel like a directory. |
| **Decision** | Tap link (`promptanatomy.app`) or save/share. | Answer poll (binary), then **Next**; honesty depends on whether Q feels tied to the post. |

---

## 3. Weakest content units (TOP 10)

| id | Problem | User mindset | Fix direction |
|----|---------|--------------|---------------|
| **114** | **90 / 10 / 1** framed as fact | “Another influencer pyramid stat” | Reframe as **illustrative tiers** (like **101**). |
| **113** | “**Top 10%**” | Same trust hit | Replace with **operators / strong users** (qualitative). |
| **9** | “**The top 10%** do…” in body | Reads as invented segmentation | Same—qualitative label. |
| **4** | “**90% of users**” in body | Undermines **101**-style hygiene | “Most casual users” or similar. |
| **27** | “**20% capacity**” | Sounds measured, isn’t | “Far below what the model can do when fully specified” (or similar). |
| **104–123** (band) | One rhythm for **20** rows | “I’ve read this card before” | Vary opener/closer or collapse redundant beats in **W4**; not all in one edit. |
| **32–99** (stack cluster) | 21× similar skeleton | “Which role was this again?” | Keep failure-mode leads; trim duplicate tool lines where identical (**deep**). |
| **1–30** (sequence) | Same **theme** ×3 | “Bot repeats” | Already mitigated by **Pass / Angle**; optional one-line **“Same headline, new angle”** in caption (**deep** / bot copy). |
| **34** | Missing **`topic_key`** | Hurts analytics and journey tooling | Set **`framework_layers_canonical`**. |
| **Early hot_or_not polls** | Low Jaccard vs long body | Tap by position / habit | Keep **`correct_option_id`** mix; tighten Q to lesson (**W3** selective). |

---

## 4. Microcopy audit

- **Bot:** [bot/bot_copy.py](../bot/bot_copy.py) — scoped commands OK; audit did not require changes.
- **Polls:** Binary choices; **39× / 59×** split on `correct_option_id` (0 vs 1) — healthy vs always-second-option.
- **theme_note:** Matches **`theme`** where set (semantics audit).
- **Gaps:** Optional one-line debrief after poll in Telegram is product behavior, not JSON—no change here.

---

## 5. Readability and clarity

- **Density:** Mean body length ~**800** chars — appropriate for mobile.
- **Cognitive load:** **Medium** on stack and dash series; **lower** on 1–30 after Pass/Angle pass.
- **2–3s scan:** **High** on 104–123; **Medium** on dense stack posts (many URLs).

---

## 6. UI/UX friction

- **Telegram:** Repetition perception on **same `theme`** three times; mitigated but not eliminated.
- **Trust:** Any **%** without source in **body** (not meme **70% OFF** headline context).
- **Choice overload:** Stack posts list many tools—acceptable for “stack” intent; weakest when two consecutive posts list nearly the same four links.

---

## 7. Trust and conversion signals

- **Strong:** **101** explicit “illustrative—not a scientific census”; **102** agency; **103** workflow framing; **100** softened product line; consistent **`https://promptanatomy.app`** close.
- **Weak:** Residual **fake-precision** phrases (see §3).
- **What happens next:** Clear CTA pattern; **Pass** lines teach **what to do this week** in stack series—good.

---

## 8. Low hanging fruits (inventory)

| Location | Issue | Specific fix | Effort | Impact |
|----------|--------|--------------|--------|--------|
| **34** | Missing `topic_key` | Add `framework_layers_canonical` | S | H |
| **4** | “90% of users” | Qualitative wording | S | H |
| **9** | “top 10%” | “People who treat prompting as design…” | S | H |
| **27** | “20% capacity” | Remove fake number | S | M |
| **113** | “Top 10%” | “Strong operators” | S | H |
| **114** | 90/10/1 pyramid | Illustrative tiers + disclaimer | S | H |
| **Polls (select)** | Distant from body | Tighten **one** question per weak pair (optional) | M | M |
| **104–123** | Samey rhythm | Rewrite **one** opener (e.g. **104**) as pilot for variation | M | M |
| **CTA** | Almost all identical close | Acceptable; optional micro-variation on **100** only | S | L |
| **CURRICULUM doc** | Stale narrative counts | Point to this file + script | S | L |
| **post_journey_order** | Fatigue cluster | Document-only: consider interleave (**W4**) | S | M |
| **theme_note** | Stays aligned | No change unless `theme` changes | — | — |

---

## 9. KISS–Marry–Kill

**Kiss (keep, light touch)**

- **Inventory parity:** 98/98 PNG + polls (scripts clean).
- **101–103, 100** — trust-forward framing.
- **1–30** Pass/Angle + shared fixable CTA.
- **35** text-to-video brief pattern.
- **Binary polls** + mixed `correct_option_id`.

**Marry (double down)**

- **34** as **canonical layers** card (reference for shortened siblings).
- **Pass / Angle** convention across **1–30**.
- **Failure-mode first line** pattern in stack posts.
- **`topic_key`** discipline (now complete once **34** is set).

**Kill / reshape (strategic—not all low effort)**

- **104–123** monotony: not “delete posts”—**reshape rhythm** or interleave queue (**W4**).
- **Duplicate tool blocks** across stacks: **merge or cross-link** in a later content pass.
- **90%** in **PNG** for **9/19/29:** Kill only when new art exists; until then **keep theme**, fix **body** only elsewhere.

---

## 10. Quick wins (HIGH ROI, ≤1 day)

1. Add **`topic_key`** on **34**.
2. Soften **4, 9, 27, 113, 114** quant / pseudo-quant language.
3. Re-run **`audit_posts_png_quizzes.py`** + **`audit_post_quiz_semantics.py`** + **`sync_queue_from_posts.py --in-place`**.
4. Spot-check **one** poll for **114** if lesson alignment feels weak after copy change (optional).
5. Update **INDEX** + **CHANGELOG** + pointer in **CURRICULUM_UX_AUDIT.md**.

---

## 11. Deep fixes (strategic)

- **Queue:** Interleave **104–123** with non-dash posts or split bands via [data/post_journey_order.json](../data/post_journey_order.json).
- **Stacks:** Role-specific **unique constraint in line 1**; trim repeated 🔹 blocks where tools match.
- **PNG / theme drift:** If body drops “90%” but art keeps it, accept minor **theme vs body** tension until assets refresh.
- **3-option polls** where lesson needs **near-miss** distractors (product/UX change—out of scope here).

---

## 12. Before / after copy (TOP 5)

**1 — Post 4 (excerpt)**  
- *Before:* “This is the mistake 90% of users make.”  
- *After:* “Most casual users make this mistake.”

**2 — Post 9 (excerpt)**  
- *Before:* “The top 10% do one thing differently:”  
- *After:* “People who treat prompting as design do one thing differently:”

**3 — Post 27 (excerpt)**  
- *Before:* “But they're using them at 20% capacity.”  
- *After:* “But they're using them far below what the model can do when the prompt is fully specified.”

**4 — Post 113 (excerpt)**  
- *Before:* “Top 10%:”  
- *After:* “Strong operators:”

**5 — Post 114 (gap block)**  
- *Before:* 90% / 10% / 1% stacked as factual tiers.  
- *After:* “Most / Some / Few” illustrative ladder + “not a census” framing (see implementation in `posts.json`).

---

## Appendix A: Wave assignment (implementation)

| Wave | Items from this audit |
|------|------------------------|
| **W1** | **34** `topic_key`; epistemic fixes **4, 9, 27, 113, 114** |
| **W2** | **104–123** rhythm diversified (body copy scan patterns, not one repeating dash scaffold) — implemented in a later pass (see [CHANGELOG.md](../CHANGELOG.md) `[Unreleased]`) |
| **W3** | No poll text change required for W1 copy edits (theme unchanged); optional Q tweaks later |
| **W4** | Journey interleave; stack deduping — **implemented** in same pass: [data/post_journey_order.json](../data/post_journey_order.json) splits **104–123**; role stacks trim repeated tool blocks via **Designer (32)** reference |

**Implemented in repo alongside this file (2026-04-05):** W1 items above + doc/index/changelog updates. **W2 / W4 / stack trim** added in a subsequent changelog entry.

---

## Appendix B: Metrics snapshot (2026-04-05)

- Posts / polls: **98 / 98**; PNG web + data: **98 / 98**.
- Post ids: **1–123** with **25** intentional numeric gaps.
- `topic_key`: **97/98** before fix; **98/98** after **34** backfill.
- `correct_option_id`: **0 → 39**, **1 → 59** (snapshot at original audit date); **later repo state:** **49 / 49** after `scripts/rotate_poll_correct_options.py` + backlog passes—re-run the one-liner in [CURRICULUM_UX_AUDIT.md](CURRICULUM_UX_AUDIT.md) §4 to verify.
- Dash-heavy block: **104–123** (20 posts). **Later mitigations:** body copy rhythm diversified (W2) and Telegram journey **interleaves** this band with other post types (W4)—see [CHANGELOG.md](../CHANGELOG.md) `[Unreleased]`.

Commands: `python scripts/audit_posts_png_quizzes.py`, `python scripts/audit_post_quiz_semantics.py`.
