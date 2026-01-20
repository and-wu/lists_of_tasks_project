import asyncio
import logging

from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
from aiogram import Bot

from application.google_sheets.service import GoogleSheetsService
from application.google_sheets.utils import extract_sheet_id
from application.poll.daily_poll_service import DailyPollService
from application.user.create_user import UserService
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard
from presentation.telegram.texts import ListView

list_view = ListView()


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
    def __init__(self, scheduler: AsyncIOScheduler, bot: Bot, service: UserService, poll_service: DailyPollService):
        self.scheduler = scheduler
        self.bot = bot
        self.service = service
        self.poll_service = poll_service

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
            hour=17,
            minute=40,
            id="daily_tasks_reset",
            replace_existing=True
        )


    def schedule_poll_for_list(self, user_id: int, list_id: int, remind_time: time):
        """
        Регистрируем отдельную задачу для конкретного списка
        """
        logging.info(
            f"[SCHEDULER] poll registered: user={user_id}, list={list_id}, time={remind_time}"
        )

        job_id = f"poll_{user_id}_{list_id}"

        async def job():
            logging.info(f"[POLL] sending poll to user={user_id}, list={list_id}")
            await self.poll_service.send_daily_poll(user_id=user_id, list_id=list_id)

        self.scheduler.add_job(
            job,
            trigger="cron",
            hour=remind_time.hour,
            minute=remind_time.minute,
            id=job_id,
            replace_existing=True
        )

    # -----------------------------
    # Удаляем задачу для конкретного списка
    # -----------------------------
    def remove_poll_for_list(self, user_id: int, list_id: int):
        job_id = f"poll_{user_id}_{list_id}"
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass

    # -----------------------------
    # Регистрируем все существующие списки при старте
    # -----------------------------
    def schedule_all_polls_on_startup(self):
        for user in self.service.get_all_users():
            for list_ in user.listoftasks:
                if list_.remind_time:
                    self.schedule_poll_for_list(
                        user_id=user.id,
                        list_id=list_.id,
                        remind_time=list_.remind_time
                    )

    # -----------------------------
    # Вспомогательная функция для динамического добавления нового списка
    # -----------------------------
    def schedule_new_list(self, user_id: int, list_id: int, remind_time: time | None):
        if remind_time:
            self.schedule_poll_for_list(user_id, list_id, remind_time)

    # -----------------------------
    # Можно добавить метод для обновления времени напоминания
    # -----------------------------
    def update_list_remind_time(self, user_id: int, list_id: int, new_time: time):
        self.remove_poll_for_list(user_id, list_id)
        self.schedule_poll_for_list(user_id, list_id, new_time)