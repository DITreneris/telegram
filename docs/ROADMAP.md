# Projekto roadmap

**Paskutinis atnaujinimas:** 2026-04-04  
**Bazinė data:** 2026-04-04 (nuo jos skaičiuojami etapai)

Šiame faile surašyti **planuojami etapai ir datos**. Tai nėra techninė sutartis: kanoninės taisyklės lieka [golden_standard.md](golden_standard.md) ir CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

## Kaip naudoti

- Bent **kartą per ketvirtį** peržiūrėkite etapus: pažymėkite, kas padaryta, atnaujinkite datas ar perkėlimus, atnaujinkite lauką **Paskutinis atnaujinimas** viršuje.
- Prieš merge: [golden_standard.md](golden_standard.md) §1 (pytest, audit, API typecheck, web build) ir operacijos — [RUNBOOK.md](RUNBOOK.md).

## Datuoti etapai

### 1. Stabilizacija ir repo švara

**Laikotarpis:** 2026-04-04 → 2026-05-31

- Uždaryti nebaigtus pakeitimus (PNG, `x_poster.py`, `.env.example`): žalia šaka — `python -m pytest`, `python scripts/audit_posts_png_quizzes.py`.
- Produkcijoje patvirtinti suplanuotą siuntimą (`ENABLE_SCHEDULED_POSTING`, teisingas `SCHEDULE_TARGET_CHAT_ID` kanalui) pagal [RUNBOOK.md](RUNBOOK.md).
- Vienas `BOT_TOKEN` ir viena Railway replika (be antro `getUpdates` proceso).

### 2. Turinio ir kurso užbaigimas

**Laikotarpis:** 2026-06-01 → 2026-08-31

- Planiniai slotai / PNG pagal [POST_IMAGES_GAP_1_100.md](POST_IMAGES_GAP_1_100.md) ir auditus (`audit_posts_png_quizzes.py`).
- Telegram modelis: **photo hook + text body** (žr. [ARCHITECTURE.md](ARCHITECTURE.md) „Image or document plus long copy“).
- Po didelių `posts.json` / `polls.json` pakeitimų — [EDUCATIONAL_POSTS.md](EDUCATIONAL_POSTS.md) batch checklist.
- Eilė iš `python scripts/sync_queue_from_posts.py`, ne rankiniu `data/content.json` redagavimu.

### 3. Operacinis patikimumas ir integracijos

**Laikotarpis:** 2026-09-01 → 2026-11-30

- `data/state.json` atsarginė kopija / procedūra po Railway redeploy ([RUNBOOK.md](RUNBOOK.md)).
- Stebėti pasirenkamą X veidrodį ([CHANGELOG.md](../CHANGELOG.md) Unreleased, [x_poster.py](../x_poster.py)).
- Jei [bot/handlers.py](../bot/handlers.py) tampa per sunkūs prižiūrėti — etapinis skaidymas moduliais (tik kai skausmas realus).

### 4. Pasirenkama ateitis (rolling)

**Nuo:** 2026-12-01

- Manifesto **v2** ar išorinė būsena (DB ir pan.) tik su aiškia migracija ir testais — žr. [ARCHITECTURE.md](ARCHITECTURE.md) „Future expansion“.
- Papildomi admin įrankiai tik su pytest padengimu ir KISS vertinimu.

## Peržiūros grafikas

Fiksuotos datos, kada verta perrašyti šį failą („padaryta / atidėta“) ir atnaujinti **Paskutinis atnaujinimas**:

- **2026-07-01**
- **2026-10-01**
- **2027-01-01**

## Susijusios nuorodos

| Temą | Dokumentas / kelias |
|------|---------------------|
| CI ir invariantai | [golden_standard.md](golden_standard.md), [INDEX.md](INDEX.md) |
| Paleidimas, Railway, triktis | [RUNBOOK.md](RUNBOOK.md) |
| Eilės generavimas | [QUEUE_SYNC.md](QUEUE_SYNC.md), [queue_manifest_sync.py](../queue_manifest_sync.py), `scripts/sync_queue_from_posts.py` |
| Optional tvarka | [data/post_journey_order.json](../data/post_journey_order.json) |
| Turinio auditas | `python scripts/audit_posts_png_quizzes.py` |
| Architektūra, KISS | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Įėjimo taškas | [AGENTS.md](../AGENTS.md) |
