import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.config import settings


# Создаем асинхронный движок
engine = create_async_engine(settings.database_url, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    """Получить сессию базы данных"""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Инициализация базы данных - создание таблиц"""
    # Создаем подключение к PostgreSQL
    conn = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port
    )

    try:
        # SQL DDL для создания таблиц согласно PRD
        create_videos_table = """
        CREATE TABLE IF NOT EXISTS videos (
            id UUID PRIMARY KEY,
            creator_id UUID,
            video_created_at TIMESTAMP,
            views_count BIGINT,
            likes_count BIGINT,
            comments_count BIGINT,
            reports_count BIGINT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """

        create_snapshots_table = """
        CREATE TABLE IF NOT EXISTS video_snapshots (
            id UUID PRIMARY KEY,
            video_id UUID REFERENCES videos(id),
            views_count BIGINT,
            likes_count BIGINT,
            comments_count BIGINT,
            reports_count BIGINT,
            delta_views_count BIGINT,
            delta_likes_count BIGINT,
            delta_comments_count BIGINT,
            delta_reports_count BIGINT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        """

        create_index = """
        CREATE INDEX IF NOT EXISTS idx_snap_time ON video_snapshots(created_at);
        """

        # Выполняем SQL по отдельности
        await conn.execute(create_videos_table)
        print("[OK] Таблица 'videos' создана")

        await conn.execute(create_snapshots_table)
        print("[OK] Таблица 'video_snapshots' создана")

        await conn.execute(create_index)
        print("[OK] Индекс 'idx_snap_time' создан")

        print("\nБаза данных успешно инициализирована")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        raise
    finally:
        await conn.close()


async def execute_scalar(query: str) -> any:
    """Выполнить SQL запрос и вернуть одно значение"""
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        return result.scalar()


async def execute_query(query: str) -> list:
    """Выполнить SQL запрос и вернуть список результатов"""
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        return result.fetchall()