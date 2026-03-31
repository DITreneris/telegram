# Trūkstami `posts.json` PNG: failai ir temos

Šaltinis: [`web/public/posts.json`](../web/public/posts.json). Katalogai: [`web/public/images/posts/`](../web/public/images/posts/) (UI), [`data/images/`](../data/images/).

Atnaujinti: `python scripts/gen_missing_post_images_md.py`

## 1. Failo **nėra** diske (nei web, nei data) – sukurti

| Failas | Post `id` | Theme (iš JSON) |
|--------|-----------|-------------------|

**Vizualinė kryptis:** ant kortelės – posto `theme` tekstas (EN); Prompt Anatomy stilius: struktūra, sluoksniai, kontrolė, „system not toy“. `90_Prompt_Anatomy.png` – vienas bendras „įrankių / stack / sluoksnių“ šablonas visiems jį naudojantiems įrašams.

## 2. Yra tik `data/images` – nukopijuok į `web/public/images/posts`

Failai jau egzistuoja; naršyklė jų nerodys, kol nėra `web/public` kopijoje.

| Failas | Post `id` | Theme |
|--------|-----------|-------|

## Related

- [`POST_IMAGES.md`](POST_IMAGES.md)
