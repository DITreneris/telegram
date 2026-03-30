# Documentation index

Master list of project documentation. **Update this file** whenever you add, rename, or remove a doc under `docs/`.

For **how** the index, changelog, and reviews fit together, see [VERSIONING.md](VERSIONING.md). Release history: [CHANGELOG.md](../CHANGELOG.md).

| Path | Audience | Summary | Last reviewed |
|------|----------|---------|---------------|
| [INDEX.md](INDEX.md) | Human, agent | This index; links to changelog and versioning policy | 2026-03-30 |
| [VERSIONING.md](VERSIONING.md) | Human, agent | Documentation management: index, archive folder, changelog (Unreleased vs version section), Last reviewed, semver notes | 2026-03-29 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Human, agent | Modules, data flow, two Telegram delivery paths (queue bot vs HTTP publish incl. optional `sendPhoto`), KISS + Marry (core contracts), manifest/state, future expansion hooks | 2026-04-03 |
| [RUNBOOK.md](RUNBOOK.md) | Human, agent | Setup, env vars (incl. optional `LOG_LEVEL`), run, tests, local bot vs web publish (text + optional image URL), troubleshooting (paths, queue vs Vercel publish, `effective_user.id` vs `ADMIN_CHAT_ID`, delivery chat, EN Telegram bot messages) | 2026-04-03 |

## Archive (non-canonical)

Historical or exploratory material; **not** the live spec. See [archive/README.md](archive/README.md).

| Path | Summary |
|------|---------|
| [archive/README.md](archive/README.md) | What belongs in `docs/archive/` and how it relates to the canonical index |
| [archive/bot_concept_notes.txt](archive/bot_concept_notes.txt) | Alternate architecture notes (e.g. cycle_length); canonical: [ARCHITECTURE.md](ARCHITECTURE.md) + `content.json` v1 |
| [archive/30_posts.txt](archive/30_posts.txt) | Legacy social posts JSON (old root filename); canonical UI data: [web/public/posts.json](../web/public/posts.json) |

**Compatibility:** [bot_concept_notes.txt](bot_concept_notes.txt) is a short pointer at the former path so old links still work.

## `.txt` files in this repo (what they are)

| Location | Role |
|----------|------|
| [../requirements.txt](../requirements.txt), [../requirements-dev.txt](../requirements-dev.txt) | **pip** dependency lists (not prose docs). Keep as `.txt` by convention. |
| [bot_concept_notes.txt](bot_concept_notes.txt) | Short redirect only; full notes in [archive/bot_concept_notes.txt](archive/bot_concept_notes.txt). |
| [archive/*.txt](archive/) | Archived snapshots / notes (see [archive/README.md](archive/README.md)). |

## Related repo files (not under `docs/`)

| Path | Summary |
|------|---------|
| [../AGENTS.md](../AGENTS.md) | Entry point: purpose, module map, Cursor rules/skills |
| [../CHANGELOG.md](../CHANGELOG.md) | Notable changes (code + material docs); Keep a Changelog style |
| [../.env.example](../.env.example) | Environment variable template and local run steps |
