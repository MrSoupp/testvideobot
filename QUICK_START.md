# Quick Start Guide - Video Analytics Bot

## Prerequisites

- Docker & Docker Compose (recommended)
- Or: Python 3.11+, PostgreSQL 15+

## Option 1: Docker (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/MrSoupp/testvideobot.git
cd testvideobot
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_api_key_here
```

### 3. Run with Docker Compose
```bash
docker-compose up -d
```

Monitor logs:
```bash
docker-compose logs -f app
```

### 4. Stop
```bash
docker-compose down
```

---

## Option 2: Local Development

### 1. Clone Repository
```bash
git clone https://github.com/MrSoupp/testvideobot.git
cd testvideobot
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with:
- `BOT_TOKEN` - from BotFather on Telegram
- `OPENAI_API_KEY` - from Z.ai API dashboard
- `POSTGRES_HOST=localhost` - for local development

### 5. Setup PostgreSQL (macOS/Linux)
```bash
# Create database
createdb -U postgres analytics_db

# Or use Docker for just the database:
docker run -d --name postgres-dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=analytics_db \
  -p 5432:5432 \
  postgres:15
```

### 6. Initialize Database & Start Bot
```bash
python run_bot.py
```

The bot will:
1. Connect to PostgreSQL
2. Initialize tables
3. Load sample data (358 videos)
4. Start listening for Telegram messages

---

## Testing the Bot

Open Telegram and send your bot a message:

```
User: "Сколько всего видео?"
Bot: "Результат: 358"

User: "На сколько просмотров выросли видео 28 ноября?"
Bot: "Результат: 14639"

User: "Сколько разных видео получали лайки 27 ноября?"
Bot: "Результат: 226"
```

---

## Troubleshooting

### Docker Issues

**Container fails to start:**
```bash
docker-compose logs app
docker-compose logs db
```

**Database connection refused:**
```bash
# Ensure health check passed
docker-compose ps
# Should show "healthy" for db service
```

### Local Issues

**"Connection refused" error:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Or restart Docker PostgreSQL:
docker restart postgres-dev
```

**Module not found:**
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### API Issues

**429 Rate limit error:**
- Check your Z.ai API quota
- Wait a few seconds and retry
- Typical usage won't hit limits

**401 Invalid API key:**
- Verify `OPENAI_API_KEY` in `.env`
- Generate new key from Z.ai dashboard

---

## Architecture

```
Telegram Message
    ↓
Bot Handler (aiogram)
    ↓
Function Calling (glm-4.6)
    ↓
Parameter Extraction
    ↓
SQL Construction (Python)
    ↓
PostgreSQL Query
    ↓
Result → Telegram Response
```

---

## Next Steps

- See [README.md](README.md) for full documentation
- Check [docs/](docs/) for detailed guides
- Run tests: `python tests/run_all_tests.py`
- Review code in [src/](src/) directory

---

## Support

- Issues? See README.md **Troubleshooting** section
- Questions? Check [docs/STATUS.md](docs/STATUS.md)
- Want to contribute? Create a pull request!

---

**Status:** Production Ready | **LLM:** glm-4.6 Function Calling | **Data:** 358 videos, 35,946 snapshots
