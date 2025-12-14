import os
import json
import logging
from datetime import datetime
from openai import AsyncOpenAI
from src.config import settings

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
try:
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url
    )
    logger.info("AsyncOpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AsyncOpenAI: {e}")
    import traceback
    traceback.print_exc()
    client = None

# --- TOOL DEFINITION (The Router) ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "build_sql_query",
            "description": "Extract parameters to build a SQL query for video analytics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["TOTAL_STATIC", "GROWTH_DYNAMIC", "UNIQUE_ACTIVE"],
                        "description": "TOTAL_STATIC for 'How many videos total'. GROWTH_DYNAMIC for 'How many views added/grew'. UNIQUE_ACTIVE for 'How many DIFFERENT videos got views'."
                    },
                    "target_table": {
                        "type": "string",
                        "enum": ["videos", "video_snapshots"],
                        "description": "Use 'videos' for static totals. Use 'video_snapshots' for growth/deltas."
                    },
                    "metric_field": {
                        "type": "string",
                        "enum": ["id", "views_count", "likes_count", "delta_views_count", "delta_likes_count", "delta_comments_count"],
                        "description": "The database column to measure. For growth, use delta_*."
                    },
                    "date_exact": {
                        "type": "string",
                        "format": "date",
                        "description": "YYYY-MM-DD for single day queries."
                    },
                    "date_from": {
                        "type": "string",
                        "format": "date",
                        "description": "Start date YYYY-MM-DD (inclusive)."
                    },
                    "date_to": {
                        "type": "string",
                        "format": "date",
                        "description": "End date YYYY-MM-DD (inclusive)."
                    },
                    "creator_id": {
                        "type": "string",
                        "description": "UUID of the creator if specified."
                    }
                },
                "required": ["intent", "target_table", "metric_field"]
            }
        }
    }
]

async def get_sql_query(user_text: str) -> str:
    """Generate SQL query using Function Calling approach"""
    if client is None:
        raise RuntimeError("OpenAI client not initialized")

    today_str = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""You are a parameter extractor for video analytics. Today is {today_str}.
Map user questions to the 'build_sql_query' function.

RULES:
1. 'Сколько всего видео?' -> intent='TOTAL_STATIC', table='videos', field='id'
2. 'На сколько выросли просмотры?' -> intent='GROWTH_DYNAMIC', table='video_snapshots', field='delta_views_count'
3. 'Сколько РАЗНЫХ видео смотрели?' -> intent='UNIQUE_ACTIVE', table='video_snapshots', field='delta_views_count'
4. For dates like '28 ноября', extract '{today_str.split("-")[0]}-11-28'.
5. Always provide intent, target_table, and metric_field.
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 1. LLM Extraction Step
            response = await client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                tools=TOOLS,
                tool_choice={"type": "function", "function": {"name": "build_sql_query"}},
                temperature=0
            )

            tool_call = response.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            logger.info(f"Extracted Params: {args}")

            # 2. Python SQL Construction Step (Safe & Valid)
            sql = ""
            conditions = []

            # Date Logic
            date_col = "video_created_at" if args['target_table'] == "videos" else "created_at"

            if args.get('date_exact'):
                conditions.append(f"{date_col}::DATE = '{args['date_exact']}'")
            elif args.get('date_from') and args.get('date_to'):
                conditions.append(f"{date_col}::DATE >= '{args['date_from']}' AND {date_col}::DATE <= '{args['date_to']}'")

            # Creator Logic
            if args.get('creator_id'):
                conditions.append(f"creator_id = '{args['creator_id']}'")

            where_str = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Query Assembly
            if args['intent'] == 'TOTAL_STATIC':
                # "Сколько видео..." -> COUNT(id)
                # "Сколько просмотров..." -> SUM(views_count)
                agg = "COUNT" if args['metric_field'] == 'id' else "SUM"
                sql = f"SELECT {agg}({args['metric_field']}) FROM {args['target_table']}{where_str}"

            elif args['intent'] == 'GROWTH_DYNAMIC':
                # "На сколько выросли..." -> SUM(delta_*)
                sql = f"SELECT COALESCE(SUM({args['metric_field']}), 0) FROM {args['target_table']}{where_str}"

            elif args['intent'] == 'UNIQUE_ACTIVE':
                # "Сколько разных видео..." -> COUNT(DISTINCT video_id) WHERE delta > 0
                if where_str:
                    where_str += f" AND {args['metric_field']} > 0"
                else:
                    where_str = f" WHERE {args['metric_field']} > 0"

                sql = f"SELECT COUNT(DISTINCT video_id) FROM {args['target_table']}{where_str}"

            logger.info(f"Constructed SQL: {sql}")
            return sql

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM Error (attempt {attempt + 1}/{max_retries}): {e}")

            # Если это последняя попытка, выбрасываем исключение
            if attempt == max_retries - 1:
                if "429" in error_msg:
                    raise RuntimeError("Сервис временно перегружен. Попробуйте задать вопрос через несколько минут.")
                elif "402" in error_msg:
                    raise RuntimeError("Недостаточно кредитов. Пожалуйста, пополните баланс.")
                elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
                    raise RuntimeError("Превышен лимит запросов к модели. Попробуйте позже.")
                else:
                    raise RuntimeError(f"Ошибка при обработке запроса: {error_msg}")

            # Ждем перед следующей попыткой
            import asyncio
            await asyncio.sleep(2 ** attempt)
