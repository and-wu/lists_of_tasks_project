import logging
from collections import defaultdict
from datetime import time, datetime

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from application.google_sheets.service import GoogleSheetsService
from application.google_sheets.utils import extract_sheet_id
from application.poll.daily_poll_service import DailyPollService
from application.scheduler.job_registry import JobRegistry
from application.user.create_user import UserService
from domain.enums.notification_type import NotificationType
from domain.enums.repeat_type import RepeatType
from domain.task_list import ListOfTasks
from presentation.telegram.keyboards.extra_keyboard import get_hide_report_keyboard
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard

# =========================================================
# APScheduler jobs
# =========================================================

async def send_list_reminder(
    *,
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
    def __init__(self, scheduler: AsyncIOScheduler, bot, service, poll_service):
        self.scheduler = scheduler
        self.bot = bot
        self.service = service
        self.poll_service = poll_service

    def upsert_list_jobs(self, task_list: ListOfTasks):
        """Создаёт или обновляет job (reminder или poll) в зависимости от notification_type"""

        # 🔥 Сначала удаляем ВСЕ старые job
        self.remove_list_jobs(task_list.owner_id, task_list.id)

        if not task_list.is_valid_reminder() or not task_list.notification_type:
            self.remove_list_jobs(task_list.owner_id, task_list.id)
            return

        if task_list.notification_type == NotificationType.REMINDER:
            self._schedule_reminder(task_list)
        elif task_list.notification_type == NotificationType.POLL:
            self._schedule_poll(task_list)

    # -------------------------
    # Reminder
    # -------------------------
    def _schedule_reminder(self, task_list: ListOfTasks):
        # ------------------ ONCE (несколько дат) ------------------
        if task_list.repeat_type == RepeatType.ONCE:

            if not task_list.run_dates:
                return

            for run_date in task_list.run_dates:
                job_id = f"reminder:{task_list.owner_id}:{task_list.id}:{int(run_date.timestamp())}"

                self.scheduler.add_job(
                    send_list_reminder,
                    trigger=DateTrigger(run_date=run_date),
                    kwargs={
                        "bot": self.bot,
                        "service": self.service,
                        "user_id": task_list.owner_id,
                        "list_id": task_list.id,
                    },
                    id=job_id
                )

            return

        # ------------------ Повторяющиеся ------------------
        job_id = f"reminder:{task_list.owner_id}:{task_list.id}"

        trigger = CronTrigger(
            hour=task_list.remind_time.hour,
            minute=task_list.remind_time.minute,
            day_of_week=task_list.get_day_of_week_expression(),
        )

        self.scheduler.add_job(
            send_list_reminder,
            trigger=trigger,
            kwargs={
                "bot": self.bot,
                "service": self.service,
                "user_id": task_list.owner_id,
                "list_id": task_list.id,
            },
            id=job_id
        )

    # -------------------------
    # Poll
    # -------------------------
    def _schedule_poll(self, task_list: ListOfTasks):
        # ------------------ ONCE (несколько дат) ------------------
        if task_list.repeat_type == RepeatType.ONCE:

            if not task_list.run_dates:
                return

            for run_date in task_list.run_dates:
                job_id = f"poll:{task_list.owner_id}:{task_list.id}:{int(run_date.timestamp())}"

                async def job(user_id=task_list.owner_id, list_id=task_list.id):
                    await self.poll_service.send_daily_poll(user_id, list_id)

                self.scheduler.add_job(
                    job,
                    trigger=DateTrigger(run_date=run_date),
                    id=job_id
                )

            return

        # ------------------ Повторяющиеся ------------------
        job_id = f"poll:{task_list.owner_id}:{task_list.id}"

        trigger = CronTrigger(
            hour=task_list.remind_time.hour,
            minute=task_list.remind_time.minute,
            day_of_week=task_list.get_day_of_week_expression(),
        )

        async def job(user_id=task_list.owner_id, list_id=task_list.id):
            await self.poll_service.send_daily_poll(user_id, list_id)

        self.scheduler.add_job(
            job,
            trigger=trigger,
            id=job_id,
            replace_existing=True
        )

    # -------------------------
    # Trigger builder
    # -------------------------
    def _build_trigger(self, task_list: ListOfTasks):
        # ONCE больше не обрабатываем тут
        if task_list.repeat_type == RepeatType.ONCE:
            raise ValueError("_build_trigger не используется для ONCE с run_dates")

        day_of_week = task_list.get_day_of_week_expression()

        return CronTrigger(
            hour=task_list.remind_time.hour,
            minute=task_list.remind_time.minute,
            day_of_week=day_of_week,
        )

    # -------------------------
    # Remove job
    # -------------------------
    def remove_list_jobs(self, user_id: int, list_id: int):
        prefixes = [
            f"reminder:{user_id}:{list_id}",
            f"poll:{user_id}:{list_id}",
        ]

        for job in self.scheduler.get_jobs():
            for prefix in prefixes:
                if job.id.startswith(prefix):
                    try:
                        self.scheduler.remove_job(job.id)
                    except Exception:
                        logging.debug(f"Job {job.id} not found")

    # -------------------------
    # Daily reset
    # -------------------------

    def schedule_daily_reset(self, hour: int = 16, minute: int = 35):
        self.scheduler.add_job(
            send_daily_reset,
            trigger="cron",
            hour=hour,
            minute=minute,
            id=JobRegistry.daily_reset(),
            replace_existing=True,
            args=[self.bot, self.service],
        )
