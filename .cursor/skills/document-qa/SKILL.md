---
name: document-qa
description: >-
  Answers questions using project documentation (docs/*, AGENTS.md), maintains
  docs/INDEX.md when docs change, and adds or reorganizes documentation when asked.
  Use when the user wants doc Q&A, a documentation audit, index updates, or new
  docs for this repository.
---

# Document Q&A and index maintenance

## Instructions

1. **Start from the index**: Read [docs/INDEX.md](../../../docs/INDEX.md) to see canonical docs and paths. For **regression / CI / invariants**, also [docs/golden_standard.md](../../../docs/golden_standard.md). For **dated long-term milestones** (planning only, not a contract), [docs/ROADMAP.md](../../../docs/ROADMAP.md).
2. **Content at scale**: Do not use [archive/30_posts.txt](../../../docs/archive/30_posts.txt) as current scope. For post/quiz/PNG counts use [web/public/posts.json](../../../web/public/posts.json), [data/polls.json](../../../data/polls.json), and `python scripts/audit_posts_png_quizzes.py`. **POST_IMAGES** + **CONTENT_INVENTORY** = actual coverage; **POST_IMAGES_GAP_1_100** = planned 1–100 slots only.
3. **Versioning and history**: Use [docs/VERSIONING.md](../../../docs/VERSIONING.md) for doc-management rules; use [CHANGELOG.md](../../../CHANGELOG.md) for what changed when.
4. **Answer from sources**: Prefer [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md), [docs/RUNBOOK.md](../../../docs/RUNBOOK.md), and [AGENTS.md](../../../AGENTS.md). Read code only when the docs are silent or you must verify behavior.
5. **Cite paths**: In answers, reference concrete files (e.g. `bot/handlers.py`, `docs/RUNBOOK.md`) so humans can navigate quickly.

## Q&A pattern

- If the answer is in the docs: summarize accurately and **cite** the doc path (and section if helpful).
- If the docs are wrong or incomplete: say so, propose a doc fix, and update [docs/INDEX.md](../../../docs/INDEX.md) if you add/remove/rename anything under `docs/`. For notable changes, add a [CHANGELOG.md](../../../CHANGELOG.md) bullet under `[Unreleased]` or the release section you ship, per [VERSIONING.md](../../../docs/VERSIONING.md).
- If the answer is not documented: state that it is not in `docs/` or `AGENTS.md`, infer from code if appropriate, then **recommend** adding a short note to `docs/` and bumping **Last reviewed** in the index row.

## When adding or restructuring documentation

- Add a row to [docs/INDEX.md](../../../docs/INDEX.md) (path, audience, summary, last reviewed date). Bump **Last reviewed** on edited rows per [VERSIONING.md](../../../docs/VERSIONING.md).
- Use **relative links** between files under `docs/`.
- Keep content factual and aligned with the code; avoid describing unimplemented features (see ARCHITECTURE “Future” section for stubs).
- If the new doc affects the entry map, update [AGENTS.md](../../../AGENTS.md) “Where to look”, **Content pipeline**, or “Cursor assets” tables, and the **Related repo files** section in [docs/INDEX.md](../../../docs/INDEX.md).

## Workflow checklist

```
- [ ] Read docs/INDEX.md (and VERSIONING.md if changing process)
- [ ] Read relevant doc(s) or AGENTS.md
- [ ] Answer with citations; or edit docs + INDEX (+ AGENTS.md if needed)
- [ ] Notable change? Add CHANGELOG.md bullet ([Unreleased] or version section per VERSIONING.md)
- [ ] Verify internal links are relative and valid
```
