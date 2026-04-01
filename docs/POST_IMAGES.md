# Post images: coverage vs `posts.json`

**Source of truth:** [web/public/posts.json](../web/public/posts.json).

Two places in this repo can hold the same **basename** (e.g. `36_Prompt_Anatomy.png`):

| Folder | Served by Vite dev / static deploy? | Typical use |
|--------|--------------------------------------|-------------|
| [web/public/images/posts/](../web/public/images/posts/) | **Yes** — URL `/images/posts/…` | Web UI + Telegram publish from production URL |
| [data/images/](../data/images/) | **No** — not exposed as static files | Local archive / staging; **copy into `web/public`** when the UI should show it |

## Refresh counts (run locally)

```bash
python scripts/audit_post_images.py
python scripts/audit_posts_png_quizzes.py
python scripts/audit_posts_png_quizzes.py --write-inventory docs/CONTENT_INVENTORY.md
```

The first script prints a **canonical inventory** (labels A–I, same definitions every run) plus detail: PNG counts, JSON coverage, image reuse across post ids, extra files on disk, and missing refs.

**Align rows to PNGs (1:1 `id` = slot from filename):** after adding or removing files under `web/public/images/posts/`, run `python scripts/merge_posts_json_from_png.py --dry-run` then `--write` to rebuild [`web/public/posts.json`](../web/public/posts.json) (preserves existing fields per `id`, adds stubs for new slots, drops rows with no matching PNG). Then run `python scripts/fill_stub_posts_and_expand_polls.py` to replace TODO bodies and sync one quiz per post in [`data/polls.json`](../data/polls.json). See [CONTENT_INVENTORY.md](CONTENT_INVENTORY.md).

## Canonical metrics (kodėl skaičiai *turi* skirtis)

Naudokite **vieną** komandą ir **tas pačias** etiketes — tada skaičiai nesiskiria nuo paleidimo iki paleidimo, kol nesikeičia failai.

| Etiketė | Ką skaičiuoja | Pastaba |
|---------|---------------|---------|
| **A** | `posts.json` masyvo elementų skaičius | „įrašų“ skaičius UI / eilėms |
| **B** | Unikalūs posto `id` | Turi sutapti su **A** |
| **C** | Unikalūs `image` failų vardai (basename) | Jei **C < A**, bent du įrašai dalijasi tuo pačiu PNG |
| **D** | `*.png` skaičius `web/public/images/posts/` | Archyvas / atsargos gali būti > **A** |
| **E** | `*.png` skaičius `data/images/` | Dažnai sutampa su **D** po sinchronizacijos |
| **I** | **D** minus tai, kas minimai `posts.json` | Paveikslėliai diske, bet šiuo metu neįtraukti į JSON |

**Trečias skaičius — ne klaida:** planinis rinkinys **1–100** (`NN_Prompt_Anatomy.png`) yra atskira ataskaita: [POST_IMAGES_GAP_1_100.md](POST_IMAGES_GAP_1_100.md) (`python scripts/gen_post_images_gap_report.py`). Ten skaičiuojama **100 slotų**, ne **A** įrašų.

## Interpreting numbers

- **Web folder** is what matters for **localhost:5173** and most Vercel web roots: if a file is only under `data/images/`, the card still **looks broken** in the browser until you copy it to `web/public/images/posts/`.
- **`web/dist/images/posts`** after `npm run build` is a build output — do not edit there; edit `web/public` and rebuild.

## Short idea for art direction

Use the post **`theme`** as the on-image headline; one Prompt Anatomy visual system; **dedicated** `NN_Prompt_Anatomy.png` per card where JSON says so; **`90_Prompt_Anatomy.png`** = one reusable “stack / roles” template for every *How X uses AI* row.

## Related

- [CONTENT_INVENTORY.md](CONTENT_INVENTORY.md) — posts vs PNG vs `data/polls.json` quiz coverage.
- Trūkstamų failų temos (lentelė): [MISSING_POST_IMAGES.md](MISSING_POST_IMAGES.md)
- Slotai 1–100 (kiek iki šimto, likusios temos): [POST_IMAGES_GAP_1_100.md](POST_IMAGES_GAP_1_100.md)
- [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md)
