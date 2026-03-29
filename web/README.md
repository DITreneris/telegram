# Socialinių postų kopijavimas (Vite)

Statinė naršyklės aplikacija: rodo įrašus iš [`public/posts.json`](public/posts.json) ir leidžia vienu paspaudimu nukopijuoti posto tekstą rankiniam publikavimui (LinkedIn, X, WhatsApp, Facebook).

## Paleisti lokaliai

```bash
cd web
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

Produkcinis išėjimas: katalogas `dist/`.

## Turinys

- Kanoninis duomenų failas šiam UI: **`public/posts.json`**. Senesnis snapshot (buvęs repo šaknyje `30_posts.txt`) saugomas [docs/archive/30_posts.txt](../docs/archive/30_posts.txt) ir gali skirtis nuo dabartinio `posts.json`.
- Redaguokite `posts.json` ir perbuildinkite (arba naudokite `npm run dev` su karštu perkrovimu).

## Vercel

1. Importuokite šį GitHub repozitoriją į Vercel.
2. **Root Directory:** `web`
3. Build Command: `npm run build` (numatytasis)
4. Output Directory: `dist` (numatytasis Vite)

Slaptų kintamųjų šiai statinei aplikacijai nereikia.
