from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
from aiogram import Bot
from application.user.create_user import UserService
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard
from presentation.telegram.texts import ListView
from presentation.telegram.keyboards.list_keyboards import get_lists_keyboard

list_view = ListView()


async def NOT_send_list_reminder(bot: Bot, user_id: int, list_id: int, service: UserService):
    task_list = service.get_list_by_id(user_id, list_id)
    if not task_list:
        return

    tasks = service.get_tasks(user_id, list_id)
    text = f"⏰ Напоминание о списке: *{task_list.title}*\n\n"
    text += "\n".join([f"- {t.value}" for t in tasks]) if tasks else "Список пуст"

    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_lists_keyboard([task_list])
        )
    except Exception:
        pass


async def send_list_reminder(bot: Bot, user_id: int, list_id: int, service):
    """
    Отправляет напоминание о конкретном списке задач пользователя.
    Используется для APScheduler.
    """
    task_list = service.get_list_by_id(user_id, list_id)
    if not task_list:
        return

    tasks = service.get_tasks(user_id, list_id)

    # Формируем текст напоминания
    text = f"⏰ Напоминание о списке: *{task_list.title}*\n"
    if not tasks:
        text += "Список пуст"

    try:
        # Пытаемся отредактировать сообщение, если нужно — можно просто отправлять новое
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id)
        )
    except TelegramBadRequest:
        # Если сообщение уже удалено или другая ошибка
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id)
        )

class ReminderScheduler:
    def __init__(self, scheduler: AsyncIOScheduler, bot: Bot, service: UserService):
        self.scheduler = scheduler
        self.bot = bot
        self.service = service

    def schedule_list_reminder(self, user_id: int, list_id: int, remind_time: time):
        job_id = f"list_{user_id}_{list_id}"

        self.scheduler.add_job(
            send_list_reminder,
            trigger="cron",
            hour=remind_time.hour,
            minute=remind_time.minute,
            args=[self.bot, user_id, list_id, self.service],
            id=job_id,
            replace_existing=True
        )

    def remove_list_reminder(self, user_id: int, list_id: int):
        job_id = f"list_{user_id}_{list_id}"
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass
