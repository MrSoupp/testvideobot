#!/bin/bash
# Video Analytics Bot - Startup Script for Linux/Mac
# Usage: ./run_bot.sh

echo "========================================================================"
echo "VIDEO ANALYTICS BOT - STARTING"
echo "========================================================================"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo ""
    echo "[WARNING] Virtual environment not activated"
    echo "Please run: source .venv/bin/activate"
    echo ""
    exit 1
fi

# Check if .env file exists
if [[ ! -f .env ]]; then
    echo ""
    echo "[ERROR] .env file not found"
    echo "Please copy .env.example to .env and fill in your credentials:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Check if required environment variables are set
if [[ -z "$BOT_TOKEN" ]]; then
    echo ""
    echo "[WARNING] BOT_TOKEN not set in .env"
    echo ""
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo ""
    echo "[WARNING] OPENAI_API_KEY not set in .env"
    echo ""
fi

# Start the bot
echo ""
echo "[1/2] Initializing database..."
python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())" 2>/dev/null
echo "[OK] Database initialized"

echo ""
echo "[2/2] Starting bot..."
echo "[OK] Bot starting, waiting for messages..."
echo ""
echo "========================================================================"
echo "Bot is now listening for messages on Telegram"
echo "Send /start to the bot to begin"
echo "Press Ctrl+C to stop"
echo "========================================================================"
echo ""

# Start the bot
python run_bot.py
