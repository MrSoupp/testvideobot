import json
import asyncio
import asyncpg
from datetime import datetime
from src.config import settings


async def load_data():
    """Загрузка данных из JSON файла в PostgreSQL"""
    # Читаем JSON файл
    with open('data/videos.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создаем подключение к PostgreSQL
    conn = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port
    )
    
    try:
        # Очищаем таблицы перед загрузкой
        await conn.execute("DELETE FROM video_snapshots")
        await conn.execute("DELETE FROM videos")
        print("Таблицы очищены")
        
        # Загружаем видео
        for video in data['videos']:
            # Конвертируем даты
            video_created_at = datetime.fromisoformat(video['video_created_at'].replace('Z', '+00:00'))
            created_at = datetime.fromisoformat(video['created_at'].replace('Z', '+00:00'))
            updated_at = datetime.fromisoformat(video['updated_at'].replace('Z', '+00:00'))
            
            # Вставляем видео
            await conn.execute("""
                INSERT INTO videos (
                    id, creator_id, video_created_at, views_count, likes_count,
                    comments_count, reports_count, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
                video['id'],
                video['creator_id'],
                video_created_at,
                video['views_count'],
                video['likes_count'],
                video['comments_count'],
                video['reports_count'],
                created_at,
                updated_at
            )
            
            # Загружаем снимки для этого видео
            for snapshot in video['snapshots']:
                # Конвертируем даты
                snapshot_created_at = datetime.fromisoformat(snapshot['created_at'].replace('Z', '+00:00'))
                snapshot_updated_at = datetime.fromisoformat(snapshot['updated_at'].replace('Z', '+00:00'))
                
                # Вставляем снимок
                await conn.execute("""
                    INSERT INTO video_snapshots (
                        id, video_id, views_count, likes_count, comments_count, reports_count,
                        delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                    snapshot['id'],
                    snapshot['video_id'],
                    snapshot['views_count'],
                    snapshot['likes_count'],
                    snapshot['comments_count'],
                    snapshot['reports_count'],
                    snapshot['delta_views_count'],
                    snapshot['delta_likes_count'],
                    snapshot['delta_comments_count'],
                    snapshot['delta_reports_count'],
                    snapshot_created_at,
                    snapshot_updated_at
                )
        
        print(f"Загружено {len(data['videos'])} видео и их снимков")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(load_data())