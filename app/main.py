import asyncio
from aiogram import Bot, Dispatcher

from app.config import settings
from app.handlers.parsing import router as parsing_router


# Создание бота
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Функция для запуска бота
async def main():
    dp.include_routers(parsing_router)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")