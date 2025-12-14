#!/usr/bin/env python3
"""
Test various SQL queries to verify database functionality
"""
import asyncio
import asyncpg
from src.config import settings
from datetime import datetime, timedelta
from decimal import Decimal


async def test_sql_queries():
    """Test various SQL queries"""

    print("=" * 80)
    print("SQL QUERIES FUNCTIONALITY TEST")
    print("=" * 80)

    # Connect to database
    conn = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port
    )

    # Define test cases: (description, sql_query, expected_type)
    test_cases = [
        (
            "Total videos count",
            "SELECT COUNT(id) FROM videos",
            int
        ),
        (
            "Total snapshots count",
            "SELECT COUNT(id) FROM video_snapshots",
            int
        ),
        (
            "Total views (sum from videos table)",
            "SELECT COALESCE(SUM(views_count), 0) FROM videos",
            (int, Decimal)
        ),
        (
            "Total likes (sum from videos table)",
            "SELECT COALESCE(SUM(likes_count), 0) FROM videos",
            (int, Decimal)
        ),
        (
            "Total comments (sum from videos table)",
            "SELECT COALESCE(SUM(comments_count), 0) FROM videos",
            (int, Decimal)
        ),
        (
            "Average views per video",
            "SELECT ROUND(AVG(views_count), 2) FROM videos",
            (float, Decimal)
        ),
        (
            "Average likes per video",
            "SELECT ROUND(AVG(likes_count), 2) FROM videos",
            (float, Decimal)
        ),
        (
            "Video with most views",
            "SELECT MAX(views_count) FROM videos",
            int
        ),
        (
            "Video with most likes",
            "SELECT MAX(likes_count) FROM videos",
            int
        ),
        (
            "Count of videos with specific creator (sample)",
            "SELECT COUNT(id) FROM videos WHERE creator_id = 'aca1061a9d324ecf8c3fa2bb32d7be63'",
            int
        ),
        (
            "Views growth on 2025-11-28",
            "SELECT COALESCE(SUM(delta_views_count), 0) FROM video_snapshots WHERE created_at::DATE = '2025-11-28'",
            (int, Decimal)
        ),
        (
            "Likes growth on 2025-11-27",
            "SELECT COALESCE(SUM(delta_likes_count), 0) FROM video_snapshots WHERE created_at::DATE = '2025-11-27'",
            (int, Decimal)
        ),
        (
            "Unique videos that got views on 2025-11-27",
            "SELECT COUNT(DISTINCT video_id) FROM video_snapshots WHERE delta_views_count > 0 AND created_at::DATE = '2025-11-27'",
            int
        ),
        (
            "Unique videos that got likes on 2025-11-28",
            "SELECT COUNT(DISTINCT video_id) FROM video_snapshots WHERE delta_likes_count > 0 AND created_at::DATE = '2025-11-28'",
            int
        ),
    ]

    try:
        passed = 0
        failed = 0

        for i, (description, sql_query, expected_type) in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {description}")
            print(f"SQL: {sql_query}")

            try:
                result = await conn.fetchval(sql_query)

                if result is None:
                    print(f"Result: NULL")
                else:
                    print(f"Result: {result} (type: {type(result).__name__})")

                if expected_type is not None and result is not None:
                    # Handle both single types and tuples of acceptable types
                    acceptable_types = expected_type if isinstance(expected_type, tuple) else (expected_type,)
                    if isinstance(result, acceptable_types):
                        print("[OK] PASSED")
                        passed += 1
                    else:
                        type_names = "/".join(t.__name__ for t in acceptable_types)
                        print(f"[FAILED] Expected {type_names}, got {type(result).__name__}")
                        failed += 1
                else:
                    print("[OK] PASSED")
                    passed += 1

            except Exception as e:
                print(f"[FAILED] Error: {e}")
                failed += 1

        print("\n" + "=" * 80)
        print(f"[SUMMARY] Passed: {passed}/{passed+failed}")
        print("=" * 80)
        return failed == 0

    finally:
        await conn.close()


if __name__ == "__main__":
    success = asyncio.run(test_sql_queries())
    exit(0 if success else 1)
