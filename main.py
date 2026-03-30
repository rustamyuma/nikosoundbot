import asyncio
import json
import os
import aiohttp
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQuery, InlineQueryResultCachedAudio
from aiogram.client.session.aiohttp import AiohttpSession

# Настройка логов — важно для отладки
logging.basicConfig(level=logging.INFO)

load_dotenv()
token = os.getenv("BOT_TOKEN")
if not token:
    exit("Ошибка: BOT_TOKEN не найден в .env")

bot = Bot(token=token)
dp = Dispatcher()

# Кэшируем звуки в оперативной памяти
def load_sounds_from_file():
    try:
        if not os.path.exists("sounds.json"):
            logging.error("Файл sounds.json не найден!")
            return []
        with open("sounds.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка при загрузке JSON: {e}")
        return []

# Загружаем один раз при старте
SOUNDS_CACHE = load_sounds_from_file()

@dp.inline_query()
async def inline_handler(query: InlineQuery):
    query_text = query.query.lower().strip()
    results = []
    
    for s in SOUNDS_CACHE:
        if query_text in s['title'].lower():
            results.append(
                InlineQueryResultCachedAudio(
                    id=str(s['id']),  # ID должен быть строкой
                    audio_file_id=s['file_id'],
                    title=s['title']
                )
            )
            
            # Лимит Telegram на один ответ — 50 результатов
            if len(results) >= 50:
                break
    
    try:
        # cache_time=1 полезен для разработки, для продакшена лучше 300+
        await query.answer(results=results, cache_time=1)
    except Exception as e:
        logging.error(f"Ошибка отправки inline-результатов: {e}")

async def main():
    logging.info("Бот запущен и готов к вайб-кодингу!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")