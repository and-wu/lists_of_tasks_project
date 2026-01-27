# import asyncio
# import logging
# from collections import defaultdict
#
# from aiogram.exceptions import TelegramBadRequest
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from datetime import time
# from aiogram import Bot
#
# from application.google_sheets.service import GoogleSheetsService
# from application.google_sheets.utils import extract_sheet_id
# from application.poll.daily_poll_service import DailyPollService
# from application.user.create_user import UserService
# from presentation.telegram.keyboards.extra_keyboard import get_hide_report_keyboard
# from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard
# from presentation.telegram.texts import ListView
#
# list_view = ListView()
#
#
# async def send_list_reminder(bot: Bot, user_id: int, list_id: int, service: UserService):
#     """
#     Отправляет напоминание о конкретном списке задач пользователя.
#     Используется для APScheduler.
#     """
#     task_list = service.get_list_by_id(user_id, list_id)
#     if not task_list:
#         return
#
#     tasks = service.get_tasks(user_id, list_id)
#
#     # Формируем текст напоминания
#     text = f"⏰ Напоминание о списке: \n*{task_list.title}*\n"
#     if not tasks:
#         text += "Список пуст"
#
#     try:
#         # Пытаемся отредактировать сообщение, если нужно — можно просто отправлять новое
#         await bot.send_message(
#             chat_id=user_id,
#             text=text,
#             parse_mode="Markdown",
#             reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id)
#         )
#     except TelegramBadRequest as e:
#         logging.warning(f"Failed to send reminder: {e}")
#
# class ReminderScheduler:
#     def __init__(self, scheduler: AsyncIOScheduler, bot: Bot, service: UserService, poll_service: DailyPollService):
#         self.scheduler = scheduler
#         self.bot = bot
#         self.service = service
#         self.poll_service = poll_service
#
#     def schedule_list_reminder(self, user_id: int, list_id: int, remind_time: time):
#         job_id = f"list_{user_id}_{list_id}"
#
#         self.scheduler.add_job(
#             send_list_reminder,
#             trigger="cron",
#             hour=remind_time.hour,
#             minute=remind_time.minute,
#             args=[self.bot, user_id, list_id, self.service],
#             id=job_id,
#             replace_existing=True
#         )
#
#
#     def remove_list_reminder(self, user_id: int, list_id: int):
#         job_id = f"list_{user_id}_{list_id}"
#         try:
#             self.scheduler.remove_job(job_id)
#         except Exception as e:
#             logging.exception("Remove list failed")
#
#
#     def schedule_daily_reset(self):
#
#         async def job():
#             data = self.service.reset_all_tasks()
#             """
#             data = {
#                 user_id: [
#                     {
#                         "username": str,
#                         "list_title": str,
#                         "task": str,
#                         "completed": bool
#                     }
#                 ]
#             }
#             """
#
#             for user_id, rows in data.items():
#                 if not rows:
#                     continue
#
#                 lines = ["🕒 *Ежедневный отчёт*\n"]
#
#                 user = self.service.get_user_by_id(user_id)
#
#                 sheets = None
#                 if user.google_sheet_url:
#                     try:
#                         sheet_id = extract_sheet_id(user.google_sheet_url)
#                         sheets = GoogleSheetsService(sheet_id)
#                         sheets.ensure_day_header()
#                     except Exception:
#                         sheets = None
#
#                 # 🔹 группируем задачи по спискам
#                 grouped = defaultdict(list)
#                 for row in rows:
#                     grouped[row["list_title"]].append(row)
#
#                 # 🔹 выводим списки без дублирования названия
#                 for list_title, tasks in grouped.items():
#                     lines.append(f"📋 *{list_title}*")
#
#                     for task in tasks:
#                         status = "✅" if task["completed"] else "❌"
#                         lines.append(f"• {task['task']} — {status}")
#
#                         if sheets:
#                             try:
#                                 sheets.append_task(
#                                     list_title=list_title,
#                                     task_value=task["task"],
#                                     completed=task["completed"]
#                                 )
#                             except Exception:
#                                 pass
#
#                     lines.append("")  # пустая строка между списками
#
#                 try:
#                     await self.bot.send_message(
#                         chat_id=user_id,
#                         text="\n".join(lines),
#                         parse_mode="Markdown",
#                         reply_markup=get_hide_report_keyboard()
#                     )
#                 except Exception as e:
#                     logging.exception("Daily reset failed")
#
#         self.scheduler.add_job(
#             job,
#             trigger="cron",
#             hour=11,
#             minute=30,
#             id="daily_tasks_reset",
#             replace_existing=True,
#         )
#
#
#     def schedule_poll_for_list(self, user_id: int, list_id: int, remind_time: time):
#         """
#         Регистрируем отдельную задачу для конкретного списка
#         """
#         logging.info(
#             f"[SCHEDULER] poll registered: user={user_id}, list={list_id}, time={remind_time}"
#         )
#
#         job_id = f"poll_{user_id}_{list_id}"
#
#         async def job():
#             logging.info(f"[POLL] sending poll to user={user_id}, list={list_id}")
#             await self.poll_service.send_daily_poll(user_id=user_id, list_id=list_id)
#
#         self.scheduler.add_job(
#             job,
#             trigger="cron",
#             hour=remind_time.hour,
#             minute=remind_time.minute,
#             id=job_id,
#             replace_existing=True
#         )
#
#     # -----------------------------
#     # Удаляем задачу для конкретного списка
#     # -----------------------------
#     def remove_poll_for_list(self, user_id: int, list_id: int):
#         job_id = f"poll_{user_id}_{list_id}"
#         try:
#             self.scheduler.remove_job(job_id)
#         except Exception:
#             pass
#
#     # -----------------------------
#     # Регистрируем все существующие списки при старте
#     # -----------------------------
#     def schedule_all_polls_on_startup(self):
#         for user in self.service.get_all_users():
#             for list_ in user.listoftasks:
#                 if list_.remind_time:
#                     self.schedule_poll_for_list(
#                         user_id=user.id,
#                         list_id=list_.id,
#                         remind_time=list_.remind_time
#                     )
#
#     # -----------------------------
#     # Вспомогательная функция для динамического добавления нового списка
#     # -----------------------------
#     def schedule_new_list(self, user_id: int, list_id: int, remind_time: time | None):
#         if remind_time:
#             self.schedule_poll_for_list(user_id, list_id, remind_time)
#
#     # -----------------------------
#     # Можно добавить метод для обновления времени напоминания
#     # -----------------------------
#     def update_list_remind_time(self, user_id: int, list_id: int, new_time: time):
#         self.remove_poll_for_list(user_id, list_id)
#         self.schedule_poll_for_list(user_id, list_id, new_time)


import logging
from collections import defaultdict
from datetime import time
from enum import Enum

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from application.google_sheets.service import GoogleSheetsService
from application.google_sheets.utils import extract_sheet_id
from application.poll.daily_poll_service import DailyPollService
from application.user.create_user import UserService
from presentation.telegram.keyboards.extra_keyboard import get_hide_report_keyboard
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard


# =========================================================
# Job registry
# =========================================================

class JobType(Enum):
    LIST_REMINDER = "list_reminder"
    LIST_POLL = "list_poll"
    DAILY_RESET = "daily_reset"


class JobRegistry:
    @staticmethod
    def list_reminder(user_id: int, list_id: int) -> str:
        return f"{JobType.LIST_REMINDER.value}:{user_id}:{list_id}"

    @staticmethod
    def list_poll(user_id: int, list_id: int) -> str:
        return f"{JobType.LIST_POLL.value}:{user_id}:{list_id}"

    @staticmethod
    def daily_reset() -> str:
        return JobType.DAILY_RESET.value


# =========================================================
# APScheduler jobs
# =========================================================

async def send_list_reminder(
    bot: Bot,
    service: UserService,
    user_id: int,
    list_id: int,
):
    task_list = service.get_list_by_id(user_id, list_id)
    if not task_list:
        logging.warning(
            f"[REMINDER] list not found: user={user_id}, list={list_id}"
        )
        return

    tasks = service.get_tasks(user_id, list_id)

    text = f"⏰ *Напоминание о списке*\n\n*{task_list.title}*\n"
    if not tasks:
        text += "\nСписок пуст"

    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id),
        )
    except TelegramBadRequest as e:
        logging.warning(
            f"[REMINDER] telegram error user={user_id}, list={list_id}: {e}"
        )


async def send_daily_reset(
    bot: Bot,
    service: UserService,
):
    data = service.reset_all_tasks()

    for user_id, rows in data.items():
        if not rows:
            continue

        user = service.get_user_by_id(user_id)
        lines = ["🕒 *Ежедневный отчёт*\n"]

        sheets = None
        if user.google_sheet_url:
            try:
                sheet_id = extract_sheet_id(user.google_sheet_url)
                sheets = GoogleSheetsService(sheet_id)
                #sheets.ensure_day_header()
                sheets.append_day_header()
            except Exception as e:
                logging.warning(
                    f"[SHEETS] init failed user={user_id}: {e}"
                )
                sheets = None

        grouped = defaultdict(list)
        for row in rows:
            grouped[row["list_title"]].append(row)

        for list_title, tasks in grouped.items():
            lines.append(f"📋 *{list_title}*")

            for task in tasks:
                status = "✅" if task["completed"] else "❌"
                lines.append(f"• {task['task']} — {status}")

                if sheets:
                    try:
                        sheets.append_task(
                            list_title=list_title,
                            task_value=task["task"],
                            completed=task["completed"],
                        )
                    except Exception as e:
                        logging.warning(
                            f"[SHEETS] append failed user={user_id}: {e}"
                        )

            # добавляем пустую строку когда список закончился
            if sheets:
                try:
                    sheets.append_empty_row()
                except Exception as e:
                    logging.warning(
                        f"[SHEETS] append empty row failed user={user_id}: {e}"
                    )

            lines.append("")

        try:
            await bot.send_message(
                chat_id=user_id,
                text="\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_hide_report_keyboard(),
            )
        except Exception as e:
            logging.warning(
                f"[RESET] failed to send report user={user_id}: {e}"
            )


async def send_poll(
    poll_service: DailyPollService,
    user_id: int,
    list_id: int,
):
    logging.info(f"[POLL] sending poll user={user_id}, list={list_id}")
    await poll_service.send_daily_poll(user_id=user_id, list_id=list_id)


# =========================================================
# Scheduler facade
# =========================================================

class ReminderScheduler:
    def __init__(
        self,
        scheduler: AsyncIOScheduler,
        bot: Bot,
        service: UserService,
        poll_service: DailyPollService,
    ):
        self.scheduler = scheduler
        self.bot = bot
        self.service = service
        self.poll_service = poll_service

    # -------------------------
    # List reminder
    # -------------------------

    def schedule_list_reminder(
        self,
        user_id: int,
        list_id: int,
        remind_time: time,
    ):
        self.scheduler.add_job(
            send_list_reminder,
            trigger="cron",
            hour=remind_time.hour,
            minute=remind_time.minute,
            id=JobRegistry.list_reminder(user_id, list_id),
            replace_existing=True,
            args=[self.bot, self.service, user_id, list_id],
        )

    def remove_list_reminder(self, user_id: int, list_id: int):
        self._remove_job(JobRegistry.list_reminder(user_id, list_id))

    # -------------------------
    # Polls
    # -------------------------

    def schedule_poll_for_list(
        self,
        user_id: int,
        list_id: int,
        remind_time: time,
    ):
        logging.info(
            f"[SCHEDULER] poll registered user={user_id}, list={list_id}, time={remind_time}"
        )

        self.scheduler.add_job(
            send_poll,
            trigger="cron",
            hour=remind_time.hour,
            minute=remind_time.minute,
            id=JobRegistry.list_poll(user_id, list_id),
            replace_existing=True,
            args=[self.poll_service, user_id, list_id],
        )

    def remove_poll_for_list(self, user_id: int, list_id: int):
        self._remove_job(JobRegistry.list_poll(user_id, list_id))

    # -------------------------
    # Daily reset
    # -------------------------

    def schedule_daily_reset(self, hour: int = 11, minute: int = 51):
        self.scheduler.add_job(
            send_daily_reset,
            trigger="cron",
            hour=hour,
            minute=minute,
            id=JobRegistry.daily_reset(),
            replace_existing=True,
            args=[self.bot, self.service],
        )

    # -------------------------
    # Startup helpers
    # -------------------------

    def schedule_all_polls_on_startup(self):
        for user in self.service.get_all_users():
            for task_list in user.listoftasks:
                if task_list.remind_time:
                    self.schedule_poll_for_list(
                        user_id=user.id,
                        list_id=task_list.id,
                        remind_time=task_list.remind_time,
                    )

    def schedule_new_list(
        self,
        user_id: int,
        list_id: int,
        remind_time: time | None,
    ):
        if remind_time:
            self.schedule_poll_for_list(user_id, list_id, remind_time)

    def update_list_remind_time(
        self,
        user_id: int,
        list_id: int,
        new_time: time,
    ):
        self.remove_poll_for_list(user_id, list_id)
        self.schedule_poll_for_list(user_id, list_id, new_time)

    # -------------------------
    # Internal
    # -------------------------

    def _remove_job(self, job_id: str):
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            logging.debug(f"[SCHEDULER] job not found: {job_id}")
