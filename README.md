# NickForge AI 🤖

> Professional Telegram Nickname Generator Bot — 20+ styles, AI-powered, 3 languages.

## Features

- 🎮 **Gaming** — PUBG, Free Fire, Valorant, CS2, Minecraft, Roblox, etc.
- 👑 **Premium** — Luxury-looking usernames
- 🔥 **Cool** — Modern, short, easy to remember
- 👻 **Invisible** — Invisible Unicode nicknames
- ⚡ **Fancy Unicode** — Mathematical script, fraktur, monospace, etc.
- 🎨 **Decorated** — Symbols around your name (꧁Avaz꧂)
- 🤖 **AI Generator** — Describe what you want, bot creates it
- 💀 **Hacker** — Byte, Null, Kernel, Cipher...
- 🐺 **Animal** / 🌌 **Anime** / 💎 **Luxury** / ❤️ **Couple** / 🌙 **Dark** / 👽 **Space** / ⚙ **Robot**
- 🔍 **Search** by keyword
- ⭐ **Favorites** with save/delete
- 📜 **History**
- 👥 **Referral system** with coins
- 🎁 **Daily bonus**
- 🏆 **Leaderboard**
- 📢 **Force Join** channels
- 📢 **Broadcast** system
- 🌐 **3 languages** — Uzbek, English, Russian
- 🔐 **Admin panel** with dashboard

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13+ |
| Framework | aiogram 3.x |
| Database | PostgreSQL + SQLAlchemy ORM + Alembic |
| Cache/FSM | Redis |
| Scheduler | APScheduler |
| Deployment | Docker / Vercel (serverless) |

## Quick Start

### Local (Docker)

```bash
cp .env.example .env
# Edit .env with your BOT_TOKEN
docker compose up -d
```

### Local (without Docker)

```bash
pip install .
python -m src.main
```

### Vercel (Serverless)

```bash
npx vercel --prod
curl -X POST https://your-app.vercel.app/setup
```

> ⚠️ On Vercel, use **cloud PostgreSQL** (Neon, Supabase) and **cloud Redis** (Upstash).

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot Token |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs |
| `DB_HOST` | PostgreSQL host |
| `DB_PASSWORD` | PostgreSQL password |
| `REDIS_HOST` | Redis host |
| `REDIS_PASSWORD` | Redis password (Upstash) |

## Project Structure

```
src/
├── domain/          # Models, enums, exceptions
├── infrastructure/  # Database, Redis, repository, scheduler
├── services/        # Business logic
├── presentation/    # Handlers, keyboards, middlewares, filters
└── utils/           # Localizer, helpers
api/                 # Vercel serverless functions
locales/             # uz.json, en.json, ru.json
```

## License

MIT
