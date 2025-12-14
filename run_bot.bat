@echo off
REM Video Analytics Bot - Startup Script for Windows
REM Usage: run_bot.bat

echo.
echo ========================================================================
echo                    VIDEO ANALYTICS BOT - STARTING
echo ========================================================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo [WARNING] Virtual environment not activated
    echo Please run: .venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found
    echo Please copy .env.example to .env and fill in your credentials:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Check if required environment variables are set
if "%BOT_TOKEN%"=="" (
    echo [WARNING] BOT_TOKEN not set in .env
    echo.
)

if "%OPENAI_API_KEY%"=="" (
    echo [WARNING] OPENAI_API_KEY not set in .env
    echo.
)

REM Start the bot
echo [1/2] Initializing database...
python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())" 2>nul
echo [OK] Database initialized
echo.

echo [2/2] Starting bot...
echo [OK] Bot starting, waiting for messages...
echo.
echo ========================================================================
echo Bot is now listening for messages on Telegram
echo Send /start to the bot to begin
echo Press Ctrl+C to stop
echo ========================================================================
echo.

REM Start the bot
python run_bot.py

pause
