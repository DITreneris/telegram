# Post PNG padengimas 1–100 (`web/public/images/posts`)

Konvencija: failo vardas `NN_Prompt_Anatomy.png`, kur `NN` = `f"{n:02d}"` (1→`01` … 9→`09`, 100→`100`).

**Šaltinis:** [`web/public/posts.json`](../web/public/posts.json) (dabar **31** eilučių — ne visi slotai 1–100 turi `theme` JSON'e).

## Santrauka

| Rodiklis | Reikšmė |
|----------|---------|
| Slotų iš viso (1–100) | 100 |
| PNG yra `web/public/images/posts/` | **72** |
| PNG **trūksta** | **28** |

## Trūkstami failai ir temos

Tema: pirmiausia `posts.json` pagal posto `id` = slotui; jei nėra eilutės — `PLANNED_THEME_BY_SLOT` skripte; kitaip — *nėra įrašo*.

| Slot | Failas | Tema | Pastaba |
|------|--------|------|---------|
| 31 | `31_Prompt_Anatomy.png` | Most people are using the wrong AI image tool. | planas (`scripts/gen_post_images_gap_report.py`) |
| 35 | `35_Prompt_Anatomy.png` | Top AI text-to-video tools (2026) | planas (`scripts/gen_post_images_gap_report.py`) |
| 40 | `40_Prompt_Anatomy.png` | Which AI app for real work? (2026 tiers) | planas (`scripts/gen_post_images_gap_report.py`) |
| 45 | `45_Prompt_Anatomy.png` | Multimodal AI: images, PDFs, screenshots (2026) | planas (`scripts/gen_post_images_gap_report.py`) |
| 50 | `50_Prompt_Anatomy.png` | Audio AI: speech ↔ text (2026) | planas (`scripts/gen_post_images_gap_report.py`) |
| 55 | `55_Prompt_Anatomy.png` | Text → music AI (2026, short) | planas (`scripts/gen_post_images_gap_report.py`) |
| 57 | `57_Prompt_Anatomy.png` | Agreement is not intelligence. It's compliance. | planas (`scripts/gen_post_images_gap_report.py`) |
| 61 | `61_Prompt_Anatomy.png` | How a Researcher uses AI: decisions & stack | planas (`scripts/gen_post_images_gap_report.py`) |
| 63 | `63_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 66 | `66_Prompt_Anatomy.png` | How a Data Analyst uses AI: decisions & stack | planas (`scripts/gen_post_images_gap_report.py`) |
| 67 | `67_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 68 | `68_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 69 | `69_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 72 | `72_Prompt_Anatomy.png` | How a CMO uses AI: decisions & stack | planas (`scripts/gen_post_images_gap_report.py`) |
| 73 | `73_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 77 | `77_Prompt_Anatomy.png` | How Operations uses AI: decisions & stack | planas (`scripts/gen_post_images_gap_report.py`) |
| 78 | `78_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 79 | `79_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 80 | `80_Prompt_Anatomy.png` | Vibe coding: idea → MVP → ship (2026) | planas (`scripts/gen_post_images_gap_report.py`) |
| 82 | `82_Prompt_Anatomy.png` | How a Software Engineer uses AI: decisions & stack | planas (`scripts/gen_post_images_gap_report.py`) |
| 83 | `83_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 85 | `85_Prompt_Anatomy.png` | AI app builders: MVP → real app (2026) | planas (`scripts/gen_post_images_gap_report.py`) |
| 87 | `87_Prompt_Anatomy.png` | How a CTO uses AI: decisions & stack | planas (`scripts/gen_post_images_gap_report.py`) |
| 88 | `88_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 90 | `90_Prompt_Anatomy.png` | The stack that actually ships products (2026); shared template for several role posts in JSON | planas (`scripts/gen_post_images_gap_report.py`) |
| 91 | `91_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 92 | `92_Prompt_Anatomy.png` | — | įrašykite `id` + `theme` į `posts.json` arba papildykite `PLANNED_THEME_BY_SLOT` |
| 100 | `100_Prompt_Anatomy.png` | You're not prompting. You're guessing. | `posts.json` |

## Atnaujinimas

```bash
python scripts/gen_post_images_gap_report.py
```

## Related

- [`POST_IMAGES.md`](POST_IMAGES.md)
- [`MISSING_POST_IMAGES.md`](MISSING_POST_IMAGES.md)
