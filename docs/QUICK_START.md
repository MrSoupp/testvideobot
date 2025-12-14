# Quick Start Guide - Video Analytics Bot

## Prerequisites
- PostgreSQL 15+ (running)
- Python 3.11+
- Valid OpenRouter API key (in .env)
- Valid Telegram bot token (in .env)

## Current Status
✓ Database initialized and populated (358 videos, 35,946 snapshots)
✓ All systems tested and working (100% pass rate)
✓ Ready for deployment

## Start the Bot

### Windows:
```bash
run_bot.bat
```

### Linux/Mac:
```bash
bash run_bot.sh
```

### Python (all platforms):
```bash
python run_bot.py
```

### Or run directly:
```bash
python src/bot.py
```

The bot will:
1. Initialize the database (creates tables if needed)
2. Start listening for Telegram messages
3. Process user queries and return analytics

## Run Tests

### All tests:
```bash
python tests/run_all_tests.py
```

### Specific tests:
```bash
python tests/test_db_connectivity.py      # Test database
python tests/test_sql_queries.py          # Test SQL execution
python tests/test_user_requests.py        # Test user scenarios
python tests/test_with_cache.py           # Test caching
```

## Example User Queries

The bot understands natural language questions like:

```
"Сколько всего видео?"
→ Result: 358

"Сколько всего просмотров?"
→ Result: 3,326,609

"На сколько просмотров выросли видео 28 ноября?"
→ Result: 14,639

"Сколько видео у креатора aca1061a9d324ecf8c3fa2bb32d7be63?"
→ Result: 47

"Сколько разных видео получали лайки 27 ноября?"
→ Result: 226
```

## Database Information

**Database Name:** analytics_db
**Host:** localhost
**Port:** 5432
**User:** postgres

**Tables:**
- `videos` - 358 records (video metadata)
- `video_snapshots` - 35,946 records (hourly snapshots)

## Configuration

Edit `.env` if needed:

```env
BOT_TOKEN=<your_telegram_bot_token>
OPENAI_API_KEY=<your_openrouter_api_key>
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=google/gemini-2.0-flash-exp:free
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=analytics_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Test Results Summary

- Database Connectivity: PASSED
- SQL Queries (14 tests): PASSED (14/14)
- User Scenarios (15 tests): PASSED (15/15)
- LLM Integration: PASSED
- Overall: 100% SUCCESS RATE

## Troubleshooting

### "Connection refused" error
- Ensure PostgreSQL is running on localhost:5432

### "Database does not exist" error
- Run: `python init_and_load.py` to initialize and load data

### "Rate limit" error from API
- Normal for free tier - cache results to reduce API calls
- Check `STATUS.md` for rate limiting details

### Import errors
- Ensure virtual environment is activated: `.venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

## Documentation

- **STATUS.md** - Current system status and test results
- **FINAL_TEST_REPORT.txt** - Comprehensive test report
- **TEST_REPORT.md** - Detailed test documentation

## Support

For more information, see the full documentation in the project root.

---

**Status: PRODUCTION READY** 🚀
