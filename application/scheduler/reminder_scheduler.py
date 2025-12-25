import contextlib
from datetime import time

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from application.user.create_user import UserService
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard


async def send_list_reminder(
    bot: Bot,
    user_id: int,
    list_id: int,
    service: UserService,
) -> None:
    """Отправляет напоминание о конкретном списке задач пользователя.

    Используется для APScheduler.
    """
    task_list = service.get_list_by_id(user_id, list_id)
    if not task_list:
        return

    tasks = service.get_tasks(user_id, list_id)

    text = f"⏰ Напоминание о списке: *{task_list.title}*\n"
    if not tasks:
        text += "Список пуст"

    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id),
        )
    except TelegramBadRequest:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id),
        )


class ReminderScheduler:
    def __init__(
        self,
        scheduler: AsyncIOScheduler,
        bot: Bot,
        service: UserService,
    ) -> None:
        self.scheduler = scheduler
        self.bot = bot
        self.service = service

    def schedule_list_reminder(
        self,
        user_id: int,
        list_id: int,
        remind_time: time,
    ) -> None:
        job_id = f"list_{user_id}_{list_id}"

        self.scheduler.add_job(
            send_list_reminder,
            trigger="cron",
            hour=remind_time.hour,
            minute=remind_time.minute,
            args=[self.bot, user_id, list_id, self.service],
            id=job_id,
            replace_existing=True,
        )

    def remove_list_reminder(self, user_id: int, list_id: int) -> None:
        job_id = f"list_{user_id}_{list_id}"
        with contextlib.suppress(Exception):
            self.scheduler.remove_job(job_id)
