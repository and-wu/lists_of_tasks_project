import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage

from application.user.create_user import UserService
from infra.factory import create_repository, DBType

from config_data.config import BOT_TOKEN
from presentation.telegram.handlers.commands import commands_router

TOKEN = "YOUR_BOT_TOKEN"



async def start():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    repo = create_repository(
        db_type=DBType.JSON,  # DBType.JSON или DBType.SQLITE
        path=Path("storage/users"))

    service = UserService(repo=repo)

    dp.include_router(commands_router)

    try:
        # Удаляем возможный вебхук и сбрасываем накопившиеся апдейты
        await bot.delete_webhook(drop_pending_updates=True)
    except TelegramBadRequest as e:
        logging.warning(f"Ошибка при удалении вебхука: {e}")

    try:
        me = await bot.me()
        print(f"Бот запущен: @{me.username} (id: {me.id})")
        print("Polling запущен...")
        await dp.start_polling(bot, service=service)
    except Exception as e:
        logging.error(f"Не удалось запустить бота: {e}")
        sys.exit(1)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("Бот остановлен вручную")






