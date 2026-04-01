"""Bodies for post ids with no text in ``data/content.generated.json`` (e.g. 62, 100).

Canonical copy for the rest of the deck lives in ``web/public/posts.json`` after
``sync_posts_json_from_generated_manifest.py``. Merge with::

    python scripts/merge_longform_posts.py
"""

from __future__ import annotations

BODIES: dict[int, str] = {
    62: """🎚️ Safety and tone live in the spec, not the vibe.

"We're a friendly brand" inside your head doesn't reach the model.

Write rules it can obey:

– words to avoid
– claims you never make
– how to handle angry customers
– escalation triggers

📋 Example:

Tone: warm, concise, never blame the user.
Do not promise refunds; offer policy link.
If legal risk: reply with holding message only.

🎯 Brand safety is constraints, not adjectives.

→ promptanatomy.app""",
    100: """⚡ You're not prompting. You're guessing. (short stack edition)

You don't need a novel.

You need a minimum viable brief:

– Role (one line)
– Audience (who decides / reads)
– Task (one sentence)
– Output shape (bullets, word cap, sections)
– One constraint that prevents generic fluff

Five lines.

Still a system—not a vibe.

❌ "Thoughts on our roadmap?"

✅ PM advisor; audience = eng lead; output = 5 risks + 3 mitigations; max 150 words; no feature suggestions without effort score.

🎯 Short stack, full control.

→ promptanatomy.app""",
}
