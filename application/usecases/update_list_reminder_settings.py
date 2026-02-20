from datetime import time, datetime
from typing import Optional

from application.poll.daily_poll_service import DailyPollService
from domain.enums.notification_type import NotificationType
from domain.task_list import ListOfTasks, RepeatType
from application.user.create_user import UserService
from application.scheduler.reminder_scheduler import ReminderScheduler


class UpdateListReminderSettingsUseCase:
    """
    Use case для обновления настроек напоминания списка.
    Позволяет:
    - включить / изменить remind_time
    - изменить repeat_type
    - установить run_date для одноразового уведомления
    - отключить напоминание (remind_time=None)
    """
    def __init__(self, user_service: UserService, scheduler: ReminderScheduler, poll_service: DailyPollService):
        self.user_service = user_service
        self.scheduler = scheduler
        self.poll_service = poll_service

    async def execute(
        self,
        user_id: int,
        list_id: int,
        *,
        remind_time: Optional[time] = None,
        repeat_type: Optional[RepeatType] = None,
        run_dates: Optional[list[datetime]] = None,
        notification_type: NotificationType | None = None,
        week_days: list[int] | None = None
    ) -> ListOfTasks:

        # Получаем список
        task_list = self.user_service.get_list_by_id(user_id, list_id)
        if task_list is None:
            raise ValueError(f"Список с id={list_id} не найден у пользователя {user_id}")

        # ------------------ 1️⃣ Обновляем remind_time ------------------
        if remind_time is not None:
            task_list.remind_time = remind_time
            # Если ONCE — пересобираем run_dates
            if task_list.repeat_type == RepeatType.ONCE and task_list.run_dates:
                task_list.run_dates = [
                    dt.replace(hour=remind_time.hour, minute=remind_time.minute)
                    for dt in task_list.run_dates
                ]

        # ------------------ 2️⃣ Обновляем repeat_type ------------------
        if repeat_type is not None:
            task_list.set_repeat_type(repeat_type)  # здесь очищаются run_dates и week_days если нужно

        # ------------------ 3️⃣ Обновляем run_dates и week_days ------------------
        current_repeat = task_list.repeat_type

        if run_dates is not None and current_repeat == RepeatType.ONCE:
            task_list.run_dates = sorted(run_dates)

        if week_days is not None and current_repeat == RepeatType.CUSTOM:
            task_list.week_days = week_days

        # ------------------ 4️⃣ Обновляем notification_type ------------------
        if notification_type is not None:
            old_type = task_list.notification_type
            task_list.notification_type = notification_type

            # POLL → REMINDER: закрываем активный опрос
            if old_type == NotificationType.POLL and notification_type == NotificationType.REMINDER:
                if task_list.is_poll_active():
                    try:
                        await self.poll_service.close_poll(task_list)
                    except Exception:
                        pass
                task_list.active_poll_id = None
                task_list.poll_voted = False

            # REMINDER → POLL: пересоздаем job для Poll
            if old_type == NotificationType.REMINDER and notification_type == NotificationType.POLL:
                # если remind_time есть, создаем job
                if task_list.is_valid_reminder():
                    self.scheduler.upsert_list_jobs(task_list)

        # ------------------ 5️⃣ Сохраняем изменения ------------------
        self.user_service.save_user(user_id)

        # ------------------ 6️⃣ Синхронизируем scheduler ------------------
        if task_list.is_valid_reminder():
            self.scheduler.upsert_list_jobs(task_list)
        else:
            self.scheduler.remove_list_jobs(user_id, list_id)

        return task_list