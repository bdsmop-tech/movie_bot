import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, room, filters, swipe, history

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(room.router)
    dp.include_router(filters.router)
    dp.include_router(swipe.router)
    dp.include_router(history.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
