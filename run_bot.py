#!/usr/bin/env python3
"""
Video Analytics Bot - Main Entry Point
Starts the Telegram bot for video analytics
"""
import asyncio
import sys
from src.database import init_db
from src.bot import main


async def startup():
    """Initialize database and start bot"""
    print("=" * 80)
    print("VIDEO ANALYTICS BOT - STARTING")
    print("=" * 80)

    try:
        print("\n[1/2] Initializing database...")
        await init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[INFO] Database initialization: {e}")
        # Continue anyway - tables might already exist

    print("\n[2/2] Starting bot...")
    print("[OK] Bot starting, waiting for messages...")
    print("\n" + "=" * 80)
    print("Bot is now listening for messages on Telegram")
    print("Send /start to the bot to begin")
    print("Press Ctrl+C to stop")
    print("=" * 80 + "\n")

    try:
        await main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped")
        sys.exit(0)
