# Documentation management and versioning

This project treats **documentation as a managed set**: indexed, reviewed, and tied to the same visibility as code changes via [CHANGELOG.md](../CHANGELOG.md).

## Roles

| Artifact | Purpose |
|----------|---------|
| [INDEX.md](INDEX.md) | Single inventory of canonical `docs/*.md`, the archive section, and pointers to root docs; **Last reviewed** per row. |
| [CHANGELOG.md](../CHANGELOG.md) | Human-readable history of **notable** code and documentation changes. |
| This file (`VERSIONING.md`) | Rules for when and how to bump doc metadata and changelog entries. |

## Document index (`INDEX.md`)

- Every new, renamed, or removed **canonical** markdown file under `docs/` (excluding `docs/archive/`, which is indexed under the Archive section) must update [INDEX.md](INDEX.md) in the **same commit or change** as the file.
- When you add or remove archived material, update the Archive table in [INDEX.md](INDEX.md) and [archive/README.md](archive/README.md) as needed.
- **Last reviewed**: set to the date (ISO `YYYY-MM-DD`) when the doc was substantively checked for accuracy against the code or when it was last meaningfully edited.

## Changelog (`CHANGELOG.md`)

- Use **`[Unreleased]`** for work not yet “released” (or merge into a dated/versioned section when you cut a release).
- Add a **changelog line** when the change would matter to someone pulling the repo: new features, breaking changes, security fixes, important bug fixes, or **material documentation changes** (new guides, wrong runbook corrected, architecture shifts).
- Skip changelog entries for typos-only or purely internal wording unless they fix incorrect operational instructions.
- Prefer categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security` (Keep a Changelog).

## Project version vs documentation

- The Python app does not yet expose a single `__version__`; until packaging adds one, **CHANGELOG headings** are the source of truth for “what shipped when.”
- Optional: when you tag `v1.0.0`, align the changelog section title with that tag and continue semver for subsequent releases.

## Workflow checklist (docs + changelog)

```
- [ ] Edit doc(s); update INDEX.md rows and Last reviewed
- [ ] If notable: add bullet under CHANGELOG `[Unreleased]` or the version section you are shipping (see **Changelog** above)
- [ ] If AGENTS.md “Where to look” should list new top-level docs, update it
```
