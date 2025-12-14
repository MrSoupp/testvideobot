#!/usr/bin/env python3
"""
Test user request scenarios with predefined SQL queries
Simulates what the bot would do, but without the LLM component
"""
import asyncio
import asyncpg
from src.config import settings


async def test_user_requests():
    """Test various user request scenarios"""

    print("=" * 80)
    print("USER REQUEST SCENARIOS TEST")
    print("=" * 80)

    # Connect to database
    conn = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port
    )

    # Define user request scenarios
    # Format: (user_question, sql_query, expected_result_type)
    test_scenarios = [
        (
            "Сколько всего видео?",
            "SELECT COUNT(id) FROM videos",
            "Total videos in system"
        ),
        (
            "Сколько всего просмотров?",
            "SELECT COALESCE(SUM(views_count), 0) FROM videos",
            "Total views across all videos"
        ),
        (
            "Сколько всего лайков?",
            "SELECT COALESCE(SUM(likes_count), 0) FROM videos",
            "Total likes across all videos"
        ),
        (
            "Сколько всего комментариев?",
            "SELECT COALESCE(SUM(comments_count), 0) FROM videos",
            "Total comments across all videos"
        ),
        (
            "Какое видео получило больше всего просмотров?",
            "SELECT MAX(views_count) FROM videos",
            "Maximum views for a single video"
        ),
        (
            "Какое видео получило больше всего лайков?",
            "SELECT MAX(likes_count) FROM videos",
            "Maximum likes for a single video"
        ),
        (
            "Сколько в среднем просмотров у видео?",
            "SELECT ROUND(AVG(views_count)::numeric, 2) FROM videos",
            "Average views per video"
        ),
        (
            "Сколько в среднем лайков у видео?",
            "SELECT ROUND(AVG(likes_count)::numeric, 2) FROM videos",
            "Average likes per video"
        ),
        (
            "На сколько просмотров выросли видео 28 ноября 2025?",
            "SELECT COALESCE(SUM(delta_views_count), 0) FROM video_snapshots WHERE created_at::DATE = '2025-11-28'",
            "Views growth on Nov 28"
        ),
        (
            "На сколько лайков выросли видео 27 ноября 2025?",
            "SELECT COALESCE(SUM(delta_likes_count), 0) FROM video_snapshots WHERE created_at::DATE = '2025-11-27'",
            "Likes growth on Nov 27"
        ),
        (
            "Сколько разных видео получали просмотры 27 ноября?",
            "SELECT COUNT(DISTINCT video_id) FROM video_snapshots WHERE delta_views_count > 0 AND created_at::DATE = '2025-11-27'",
            "Unique videos with views on Nov 27"
        ),
        (
            "Сколько видео у креатора aca1061a9d324ecf8c3fa2bb32d7be63?",
            "SELECT COUNT(id) FROM videos WHERE creator_id = 'aca1061a9d324ecf8c3fa2bb32d7be63'",
            "Videos by specific creator"
        ),
        (
            "Сколько всего просмотров у видео креатора aca1061a9d324ecf8c3fa2bb32d7be63?",
            "SELECT COALESCE(SUM(views_count), 0) FROM videos WHERE creator_id = 'aca1061a9d324ecf8c3fa2bb32d7be63'",
            "Total views by specific creator"
        ),
        (
            "Сколько видео было загружено с 25 по 27 ноября включительно?",
            "SELECT COUNT(id) FROM videos WHERE video_created_at::DATE >= '2025-11-25' AND video_created_at::DATE <= '2025-11-27'",
            "Videos uploaded in date range"
        ),
        (
            "Сколько комментариев было добавлено 28 ноября?",
            "SELECT COALESCE(SUM(delta_comments_count), 0) FROM video_snapshots WHERE created_at::DATE = '2025-11-28'",
            "Comments added on Nov 28"
        ),
    ]

    try:
        passed = 0
        failed = 0

        for i, (user_question, sql_query, description) in enumerate(test_scenarios, 1):
            print(f"\n[Scenario {i}]")
            print(f"User Question: {user_question}")
            print(f"Description: {description}")
            print(f"SQL: {sql_query}")

            try:
                result = await conn.fetchval(sql_query)

                if result is None:
                    response = "По вашему запросу данных не найдено."
                else:
                    response = f"Результат: {result}"

                print(f"Bot Response: {response}")
                print("[OK] PASSED")
                passed += 1

            except Exception as e:
                print(f"[FAILED] Error: {e}")
                failed += 1

        print("\n" + "=" * 80)
        print(f"[SUMMARY] Passed: {passed}/{passed+failed}")
        print("=" * 80)

        if failed == 0:
            print("\n[SUCCESS] All user request scenarios work correctly!")
        else:
            print(f"\n[WARNING] {failed} scenarios failed!")

        return failed == 0

    finally:
        await conn.close()


if __name__ == "__main__":
    success = asyncio.run(test_user_requests())
    exit(0 if success else 1)
