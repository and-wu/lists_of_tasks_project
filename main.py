import asyncio
import contextlib
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from application.scheduler.reminder_scheduler import ReminderScheduler
from application.user.create_user import UserService
from config_data.config import BOT_TOKEN
from infra.factory import DBType, create_repository
from presentation.telegram.handlers.commands import commands_router
from presentation.telegram.handlers.list_handlers import router as list_callbacks_router
from presentation.telegram.handlers.task_handlers import router as task_callbacks_router


async def start() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    repo = create_repository(
        db_type=DBType.JSON,  # DBType.JSON или DBType.SQLITE
        path=Path("storage/users"),
    )

    # ⏰ APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()

    # сервисы
    service = UserService(repo=repo)
    reminder_scheduler = ReminderScheduler(
        scheduler=scheduler,
        bot=bot,
        service=service,
    )

    # ❗ Кладём в dp (чтобы доставать в хэндлерах)
    dp["reminder_scheduler"] = reminder_scheduler
    dp["user_service"] = service

    dp.include_router(commands_router)
    dp.include_router(list_callbacks_router)
    dp.include_router(task_callbacks_router)

    try:
        # Удаляем возможный вебхук и сбрасываем накопившиеся апдейты
        await bot.delete_webhook(drop_pending_updates=True)
    except TelegramBadRequest as e:
        logging.warning(f"Ошибка при удалении вебхука: {e}")

    try:
        await bot.me()
        await dp.start_polling(bot, service=service)
    except Exception as e:
        logging.exception(f"Не удалось запустить бота: {e}")
        sys.exit(1)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(start())






