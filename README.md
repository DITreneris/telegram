# 63 Telegram bot (lean orkestratorius)

Admin-only Telegram botas (MVP): eilė iš `data/content.json`, būsena `data/state.json`, komandos `/start`, `/next`, `/status`.

## Kur skaityti toliau

- **[AGENTS.md](AGENTS.md)** — modulių žemėlapis, Cursor taisyklės ir skills, kaip paleisti botą.
- **[docs/RUNBOOK.md](docs/RUNBOOK.md)** — aplinka, trikčių šalinimas, manifestas, **Railway** (produkcinis queue bot).

Detalės čia nekartojamos, kad nesidubliuotų su RUNBOOK.

## Trumpai

1. `python -m venv .venv`, aktyvuoti, `pip install -r requirements.txt`.
2. `.env` iš `.env.example` su `BOT_TOKEN` ir `ADMIN_CHAT_ID`.
3. Iš repo šaknies: `python run.py`.

Testams: žr. [AGENTS.md](AGENTS.md) ir [docs/RUNBOOK.md](docs/RUNBOOK.md#running-tests).
