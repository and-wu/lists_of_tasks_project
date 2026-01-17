from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
from aiogram import Bot

from application.google_sheets.service import GoogleSheetsService
from application.google_sheets.utils import extract_sheet_id
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
            reply_markup=get_lists_keyboard([task_list])
        )
    except Exception:
        pass


async def send_list_reminder(bot: Bot, user_id: int, list_id: int, service: UserService):
    """
    Отправляет напоминание о конкретном списке задач пользователя.
    Используется для APScheduler.
    """
    task_list = service.get_list_by_id(user_id, list_id)
    if not task_list:
        return

    tasks = service.get_tasks(user_id, list_id)

    # Формируем текст напоминания
    text = f"⏰ Напоминание о списке: \n*{task_list.title}*\n"
    if not tasks:
        text += "Список пуст"

    try:
        # Пытаемся отредактировать сообщение, если нужно — можно просто отправлять новое
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id)
        )
    except TelegramBadRequest:
        # Если сообщение уже удалено или другая ошибка
        await bot.send_message(
            chat_id=user_id,
            text=text,
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

    def schedule_daily_reset(self):

        async def job():
            data = self.service.reset_all_tasks()
            """
            data = {
                user_id: [
                    {
                        "username": str,
                        "list_title": str,
                        "task": str,
                        "completed": bool
                    }
                ]
            }
            """

            for user_id, rows in data.items():
                if not rows:
                    continue

                lines = ["🕒 *Ежедневный отчёт*\n"]

                # 🔹 получаем пользователя
                user = self.service.get_user_by_id(user_id)

                # 🔹 Google Sheets сервис (если есть таблица)
                sheets = None
                if user.google_sheet_url:
                    try:
                        sheet_id = extract_sheet_id(user.google_sheet_url)
                        sheets = GoogleSheetsService(sheet_id)
                        # 🔥 заголовок дня
                        sheets.ensure_day_header()
                    except Exception:
                        sheets = None  # не ломаем весь job

                for row in rows:
                    status = "✅" if row["completed"] else "❌"

                    lines.append(
                        f"📋 {row['list_title']}\n"
                        f"• {row['task']} — {status}"
                    )

                    # 🔹 пишем в Google Sheets (если сервис есть)
                    if sheets:
                        try:
                            sheets.append_task(
                                list_title=row["list_title"],
                                task_value=row["task"],
                                completed=row["completed"]
                            )
                        except Exception:
                            pass

                # 🔹 отправляем сообщение пользователю
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text="\n".join(lines),
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass

        self.scheduler.add_job(
            job,
            trigger="cron",
            hour=13,
            minute=33,
            id="daily_tasks_reset",
            replace_existing=True
        )
