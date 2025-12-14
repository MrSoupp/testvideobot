#!/usr/bin/env python3
"""
Test bot functionality with caching to avoid rate limiting
"""
import asyncio
import asyncpg
from src.config import settings
from src.llm_engine import get_sql_query
import time

# Simple cache
query_cache = {}


async def get_sql_cached(user_text: str) -> str:
    """Get SQL query with caching"""
    if user_text in query_cache:
        print(f"[CACHE HIT] Using cached SQL for: {user_text}")
        return query_cache[user_text]

    print(f"[API CALL] Fetching SQL from LLM for: {user_text}")
    sql = await get_sql_query(user_text)
    query_cache[user_text] = sql
    return sql


async def test_with_cache():
    """Test bot with SQL caching"""

    print("=" * 80)
    print("BOT TEST WITH CACHING - AVOIDING RATE LIMITS")
    print("=" * 80)

    # Test queries - same query twice to test caching
    test_queries = [
        ("Сколько всего видео?", "Counting total videos"),
        ("Сколько всего просмотров?", "Counting total views"),
        ("Сколько всего видео?", "Testing cache - same query again"),
    ]

    # Connect to database for verification
    conn = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port
    )

    try:
        for i, (query, description) in enumerate(test_queries, 1):
            print(f"\n[Test {i}] {description}")
            print(f"User Query: {query}")
            print("-" * 80)

            try:
                # Wait between requests to avoid rate limiting
                if i > 1:
                    print("Waiting 5 seconds before next request...")
                    await asyncio.sleep(5)

                # Get SQL (cached or from API)
                start = time.time()
                generated_sql = await get_sql_cached(query)
                elapsed = time.time() - start

                print(f"Generated SQL: {generated_sql}")
                print(f"Time: {elapsed:.2f}s")

                # Execute SQL and get result
                result = await conn.fetchval(generated_sql)
                print(f"Result: {result}")
                print("[OK] Test passed")

            except Exception as e:
                print(f"[FAILED] Error: {e}")

        print("\n" + "=" * 80)
        print("[COMPLETE] Tests with Caching")
        print(f"Queries cached: {len(query_cache)}")
        print("=" * 80)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_with_cache())
