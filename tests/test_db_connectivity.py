#!/usr/bin/env python3
"""
Test database connectivity and basic queries
"""
import asyncio
import asyncpg
from src.config import settings


async def test_db_connectivity():
    """Test database connection and run basic queries"""

    print("=" * 60)
    print("DATABASE CONNECTIVITY TEST")
    print("=" * 60)

    # Connect to database
    print("\n[1/5] Connecting to database...")
    try:
        conn = await asyncpg.connect(
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            host=settings.postgres_host,
            port=settings.postgres_port
        )
        print("[OK] Connected successfully")
    except Exception as e:
        print(f"[FAILED] Connection error: {e}")
        return False

    try:
        # Test 1: Count videos
        print("\n[2/5] Checking videos table...")
        video_count = await conn.fetchval("SELECT COUNT(*) FROM videos")
        print(f"[OK] Total videos: {video_count}")

        # Test 2: Count snapshots
        print("\n[3/5] Checking video_snapshots table...")
        snapshot_count = await conn.fetchval("SELECT COUNT(*) FROM video_snapshots")
        print(f"[OK] Total snapshots: {snapshot_count}")

        # Test 3: Get sample video with most views
        print("\n[4/5] Getting video with most views...")
        top_video = await conn.fetchrow(
            "SELECT id, creator_id, views_count, likes_count FROM videos ORDER BY views_count DESC LIMIT 1"
        )
        if top_video:
            print(f"[OK] Top video:")
            print(f"     ID: {top_video['id']}")
            print(f"     Creator: {top_video['creator_id']}")
            print(f"     Views: {top_video['views_count']}")
            print(f"     Likes: {top_video['likes_count']}")

        # Test 4: Get statistics
        print("\n[5/5] Getting database statistics...")
        stats = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT v.id) as total_videos,
                COUNT(vs.id) as total_snapshots,
                AVG(v.views_count) as avg_views,
                MAX(v.views_count) as max_views,
                AVG(v.likes_count) as avg_likes,
                MAX(v.likes_count) as max_likes
            FROM videos v
            LEFT JOIN video_snapshots vs ON v.id = vs.video_id
        """)

        if stats:
            print(f"[OK] Statistics:")
            print(f"     Total Videos: {stats['total_videos']}")
            print(f"     Total Snapshots: {stats['total_snapshots']}")
            print(f"     Avg Views: {stats['avg_views']:.0f}")
            print(f"     Max Views: {stats['max_views']}")
            print(f"     Avg Likes: {stats['avg_likes']:.1f}")
            print(f"     Max Likes: {stats['max_likes']}")

        print("\n" + "=" * 60)
        print("[SUCCESS] Database connectivity test passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"[FAILED] Query error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await conn.close()


if __name__ == "__main__":
    success = asyncio.run(test_db_connectivity())
    exit(0 if success else 1)
