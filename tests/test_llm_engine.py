#!/usr/bin/env python3
"""
Test LLM Engine - SQL generation
"""
import asyncio
import asyncpg
from src.config import settings
from src.llm_engine import get_sql_query


async def test_llm_engine():
    """Test LLM engine with various user queries"""

    print("=" * 70)
    print("LLM ENGINE TEST - SQL GENERATION")
    print("=" * 70)

    # Test queries
    test_queries = [
        "Сколько всего видео?",
        "Сколько всего просмотров?",
        "Сколько видео у креатора aca1061a9d324ecf8c3fa2bb32d7be63?",
        "На сколько просмотров выросли все видео 28 ноября?",
        "Сколько разных видео получали лайки 27 ноября?",
        "Сколько комментариев в среднем на видео?",
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
            print("-" * 70)

            try:
                # Generate SQL
                print("Generating SQL...")
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

        print("\n" + "=" * 70)
        print("[COMPLETE] LLM Engine Tests")
        print("=" * 70)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_llm_engine())
