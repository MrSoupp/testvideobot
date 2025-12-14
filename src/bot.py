import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.config import settings
from src.database import init_db, execute_scalar
from src.llm_engine import get_sql_query

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для аналитики видео.\n\n"
        "Задайте мне вопрос о статистике видео, например:\n"
        "• Сколько всего видео?\n"
        "• Сколько всего просмотров?\n"
        "• Сколько лайков прибавилось 28 ноября 2025?\n"
        "• Сколько комментариев было за 27 ноября 2025?"
    )


@dp.message()
async def handle_text_message(message: types.Message):
    """Обработчик текстовых сообщений"""
    try:
        # Отправляем сообщение о том, что обрабатываем запрос
        processing_msg = await message.answer("🔄 Обрабатываю ваш запрос...")
        
        # Генерируем SQL запрос с помощью LLM
        generated_sql = await get_sql_query(message.text)
        print(f"Сгенерированный SQL: {generated_sql}")
        
        # Выполняем SQL запрос
        result = await execute_scalar(generated_sql)
        
        # Удаляем сообщение об обработке
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
        # Отправляем результат
        if result is not None:
            await message.answer(f"📊 Результат: {result}")
        else:
            await message.answer("📊 По вашему запросу данных не найдено.")
            
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        
        # Удаляем сообщение об обработке, если оно существует
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )
        except:
            pass
        
        # Отправляем более информативное сообщение об ошибке
        if "сервис временно перегружен" in str(e).lower():
            await message.answer("⏳ Сервис временно перегружен. Попробуйте задать вопрос через несколько минут.")
        elif "превышен лимит запросов" in str(e).lower():
            await message.answer("⚠️ Превышен лимит запросов к модели. Попробуйте позже.")
        else:
            await message.answer("❌ Не удалось обработать запрос. Попробуйте переформулировать вопрос.")


async def main():
    """Главная функция запуска бота"""
    # Инициализируем базу данных
    await init_db()
    
    # Запускаем бота
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())