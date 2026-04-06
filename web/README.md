# Socialinių postų kopijavimas (Vite)

Statinė naršyklės aplikacija: rodo įrašus iš [`public/posts.json`](public/posts.json), susietas apklausas iš [`public/polls.json`](public/polls.json) (generuojamas build metu), ir leidžia vienu paspaudimu nukopijuoti posto tekstą rankiniam publikavimui (LinkedIn, X, WhatsApp, Facebook).

## Paleisti lokaliai

```bash
cd web
npm install
npm run dev
```

Prieš `dev` / `build` automatiškai paleidžiamas [`../scripts/sync_polls_to_web.mjs`](../scripts/sync_polls_to_web.mjs): kopijuoja kanoninį [`../data/polls.json`](../data/polls.json) → `public/polls.json`. Jei `data/polls.json` trūksta, komanda nutrūks su klaida.

## Build

```bash
npm run build
npm run preview
```

Produkcinis išėjimas: katalogas `dist/`.

Vercel (repo šaknis): [`vercel.json`](../vercel.json) `buildCommand` taip pat paleidžia `sync_polls_to_web.mjs` prieš `web` build.

## Turinys

- Kanoninis duomenų failas šiam UI: **`public/posts.json`**. Senesnis snapshot (buvęs repo šaknyje `30_posts.txt`) saugomas [docs/archive/30_posts.txt](../docs/archive/30_posts.txt) ir gali skirtis nuo dabartinio `posts.json`.
- **Apklausos:** kanonas repozitorijoje — [`data/polls.json`](../data/polls.json). `public/polls.json` yra **generuojamas** (žr. `.gitignore`); necommitinkite jo rankiniu būdu.
- Redaguokite `posts.json` ir perbuildinkite (arba naudokite `npm run dev` su karštu perkrovimu).
- UI: įrašą su `image` galima **atsisiųsti** (rankiniam įkėlimui kartu su nukopijuotu tekstu); **Publikuoti į Telegram** siunčia ir paveikslėlį (`sendPhoto`), jei `image` nurodytas — URL turi būti **to paties domeno** kaip svetainė (Telegram atsisiunčia failą viešai). Posto **tekstą** galima pataisyti tik **šioje naršyklės sesijoje** (perkrovus puslapį vėl bus `posts.json` turinys).
- **Valdikliai:** paieška (tema, tekstas, `topic_key`), rūšiavimas (eilė kaip faile, pagal `id`, pagal temą A–Z), filtras pagal temą, filtras **publikuota / nepublikuota** (žr. žemiau).
- **Žyma „Publikuota“:** po sėkmingo **Publikuoti į Telegram** įrašoma į naršyklės **`localStorage`** (`socialPostsPublished`) — tai ne Telegram istorija ir ne sinchronizuojama tarp įrenginių; skirta vietiniam darbo eigai.
- Jei įraše yra **`topic_key`**, rodomas atitinkamas ženkliukas. Prie įrašų su `related_post_id` iš `polls.json` rodomas **Apklausa (quiz)** blokas (klausimas, variantai, teisingas atsakymas peržiūrai, `theme_note`).

## Vercel

1. Importuokite šį GitHub repozitoriją į Vercel.
2. **Root Directory:** palikite tuščią (repozitorijos šaknis), kad veiktų šaknies [`vercel.json`](../vercel.json) ir Telegram `api/publish`. Jei nenaudojate publikavimo į Telegram, galite nustatyti Root į `web` ir buildinti rankiniu būdu (`npm run build`, output `dist`).
3. Su šaknies `vercel.json`: `installCommand` / `buildCommand` / `outputDirectory: web/dist` nustatyti automatiškai.

### Įdiegta (pavyzdiniai URL)

- **Pagrindinis atviras adresas:** [https://telegram-nine-tau.vercel.app](https://telegram-nine-tau.vercel.app)
- Vercel tam pačiam projektui gali rodyti ir kitus `*.vercel.app` hostname’us (pvz. Git šakai ar konkrečiam deployment’ui). Pavyzdžiai:
  - [https://telegram-git-main-tomasstaniulis76-1305s-projects.vercel.app](https://telegram-git-main-tomasstaniulis76-1305s-projects.vercel.app) (šakos deployment)
  - [https://telegram-3rc41302u-tomasstaniulis76-1305s-projects.vercel.app](https://telegram-3rc41302u-tomasstaniulis76-1305s-projects.vercel.app) (unikalus deployment URL)
- **Telegram publish API:** reliatyvus kelias `/api/publish`; pilnas pavyzdys: `https://telegram-nine-tau.vercel.app/api/publish`.
- Kai UI ir API tarnaujami iš **to paties hosto** (kaip čia), naršyklėje dažnai pakanka numatytojo elgesio be `VITE_PUBLISH_API_URL` (užklausos į `/api/publish`). Nustatykite `VITE_PUBLISH_API_URL`, jei statiniai failai kraunami iš kito origin arba testuojate API ne per tą patį domeną.

## Publikuoti į Telegram (Vercel)

Naršyklė negali saugoti `BOT_TOKEN`. Siuntimą vykdo serverless funkcija repozitorijos šaknyje: [`api/publish.ts`](../api/publish.ts).

1. Vercel projekto šaknis turi būti **visa repozitorija** (ne tik `web`), kad veiktų `vercel.json` ir `api/`.
2. Vercel **Environment Variables**: `TELEGRAM_BOT_TOKEN` (arba `BOT_TOKEN`), `TELEGRAM_PUBLISH_CHAT_ID` arba `PUBLISH_CHAT_ID` (kanalas ar pokalbis, kur botas gali rašyti), `PUBLISH_BEARER_TOKEN` (ilgas atsitiktinis stringas).
3. Pirmą kartą paspaudus „Publikuoti į Telegram“, naršyklė paprašys to paties rakto kaip `PUBLISH_BEARER_TOKEN` (įrašomas į `sessionStorage`). Neprivaloma: `web/.env` su `VITE_PUBLISH_BEARER_TOKEN` — **raktas matysis JS rinkinyje**, naudokite tik jei suprantate riziką.

**Saugumas (prod):** naudokite **ilgą atsitiktinį** `PUBLISH_BEARER_TOKEN`; produkcinėje statinėje build’e **neįdėkite** jo į `VITE_*` (raktas patektų į naršyklės JS). Repozitorijoje nėra serverless **rate limit** — apsauga nuo piktnaudžiavimo priklauso nuo stipraus bearer ir stebėsenos (žr. anglišką skiltį **Publish API security** [docs/RUNBOOK.md](../docs/RUNBOOK.md)).

Ilgas tekstas: iki **1024** simbolių eina į nuotraukos **caption** (jei yra `photo`), likutis — atskiromis žinutėmis (iki **4096** simbolių kiekvienai). Jei `VITE_PUBLISH_API_URL` rodo į **kitą domeną** nei statiniai failai, paveikslėlio URL turi būti absoliutus ir to **paties host**, kurį mato `api/publish` (dažniausiai laikyk UI ir API ant to paties Vercel host). Pats `sendPhoto` vyksta su **serverio multipart**; maži failai (≤~3MB) naršyklėje įkeliami ir siunčiami kaip **base64**, kad veiktų su **Vercel Deployment Protection** (serverio `fetch` į statiką kitaip gauna HTTP 401). Dideliems failams arba be base64 kelio: Vercel env **`VERCEL_AUTOMATION_BYPASS_SECRET`** (arba **`PUBLISH_STATIC_BYPASS_SECRET`**) — tas pats slaptas raktas kaip *Protection Bypass for Automation*; serveris prideda ant statikos `fetch` headerį **`x-vercel-protection-bypass`**.

**Pastaba:** Vite 8 reikalauja Node **≥20.19**. Repozitorijoje oficialiai naudojamas **Node 22** ([`../.nvmrc`](../.nvmrc), `engines.node`: `22.x` šaknyje ir `web/`): lokaliai paleiskite `nvm use` (arba atitikmenį), kad sutaptų su Vercel. Jei liekate ant Node 20.x, `npm` gali rodyti `EBADENGINE`, bet build dažnai vis tiek pavyksta.
