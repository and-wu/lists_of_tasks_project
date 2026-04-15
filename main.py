import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from application.poll.daily_poll_service import DailyPollService
from application.scheduler.reminder_scheduler import ReminderScheduler
from application.usecases.sync_list_reminder import SyncListReminderWithSchedulerUseCase
from application.usecases.update_list_reminder_settings import UpdateListReminderSettingsUseCase
from application.user.create_user import UserService
from infra.factory import create_repository, DBType

from config_data.config import BOT_TOKEN, PROXY
from presentation.telegram.handlers.commands import commands_router
from presentation.telegram.handlers.list_handlers import router as list_callbacks_router
from presentation.telegram.handlers.task_handlers import router as task_callbacks_router
from presentation.telegram.handlers.poll_handlers import router as poll_callbacks_router
from presentation.telegram.handlers.google_sheet_handlers import router as google_sheet_router
from presentation.telegram.handlers.weekdays_handlers import router as weekdays_router
from presentation.telegram.handlers.calendar_handler import router as calendar_router
from aiogram.client.session.aiohttp import AiohttpSession


async def start():

    session = AiohttpSession(
        proxy=PROXY
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    bot = Bot(token=BOT_TOKEN,
              session=session,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # repo = create_repository(
    #     db_type=DBType.JSON,  # DBType.JSON или DBType.SQLITE
    #     path=Path(""/app/data/db.json""))

    repo = create_repository(
        db_type=DBType.SQLITE,  # DBType.JSON или DBType.SQLITE
        path=Path("/app.db"))


    # сервисы
    service = UserService(repo=repo)
    poll_service = DailyPollService(bot=bot, user_service=service)

    # ⏰ APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()

    reminder_scheduler = ReminderScheduler(
        scheduler=scheduler,
        bot=bot,
        service=service,
        poll_service=poll_service,
    )

    # Создаём use cases
    update_reminder_uc = UpdateListReminderSettingsUseCase(user_service=service,
                                                           scheduler=reminder_scheduler,
                                                           poll_service=poll_service)
    sync_use_case = SyncListReminderWithSchedulerUseCase(user_service=service,
                                                         scheduler=reminder_scheduler)

    sync_use_case.execute()

    # системная задача
    reminder_scheduler.schedule_daily_reset()


    # ❗ Кладём в dp (чтобы доставать в хэндлерах)
    dp["reminder_scheduler"] = reminder_scheduler
    dp["user_service"] = service
    dp["poll_service"] = poll_service
    dp["update_reminder_uc"] = update_reminder_uc
    dp["sync_use_case"] = sync_use_case

    dp.include_router(commands_router)
    dp.include_router(list_callbacks_router)
    dp.include_router(task_callbacks_router)
    dp.include_router(poll_callbacks_router)
    dp.include_router(google_sheet_router)
    dp.include_router(weekdays_router)
    dp.include_router(calendar_router)

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






