#!/usr/bin/env python3
"""
Test LLM engine with real API key
"""
import asyncio
import asyncpg
from src.config import settings
from src.llm_engine import get_sql_query


async def test_llm_with_api():
    """Test LLM engine with actual API calls"""

    print("=" * 80)
    print("LLM ENGINE TEST WITH REAL API")
    print("=" * 80)

    # Test queries
    test_queries = [
        "Сколько всего видео?",
        "Сколько всего просмотров?",
        "На сколько просмотров выросли все видео 28 ноября?",
        "Сколько разных видео получали лайки 27 ноября?",
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
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Test {i}] User Query: {query}")
            print("-" * 80)

            try:
                # Generate SQL with LLM
                print("Generating SQL with LLM...")
                generated_sql = await get_sql_query(query)
                print(f"Generated SQL: {generated_sql}")

                # Execute SQL and get result
                print("Executing SQL...")
                result = await conn.fetchval(generated_sql)
                print(f"Result: {result}")
                print("[OK] Test passed")

            except Exception as e:
                print(f"[FAILED] Error: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("[COMPLETE] LLM Engine Tests with API")
        print("=" * 80)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_llm_with_api())
