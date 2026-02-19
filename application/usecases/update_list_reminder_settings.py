from datetime import time, datetime
from typing import Optional

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
    def __init__(self, user_service: UserService, scheduler: ReminderScheduler):
        self.user_service = user_service
        self.scheduler = scheduler

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

        # Обновляем напоминание
        if remind_time is not None:
            task_list.remind_time = remind_time

            # 🔥 ВАЖНО: если ONCE — пересобираем run_dates
            if task_list.repeat_type == RepeatType.ONCE and task_list.run_dates:
                new_run_dates = []

                for dt in task_list.run_dates:
                    new_dt = dt.replace(
                        hour=remind_time.hour,
                        minute=remind_time.minute
                    )
                    new_run_dates.append(new_dt)

                task_list.run_dates = sorted(new_run_dates)

        if repeat_type is not None:
            task_list.repeat_type = repeat_type

        if run_dates is not None:
            task_list.run_dates = sorted(run_dates)

        # Смена типа уведомления
        if notification_type is not None:
            old_type = task_list.notification_type
            task_list.notification_type = notification_type

            # 🔥 Если меняем POLL → REMINDER
            if old_type == NotificationType.POLL and notification_type == NotificationType.REMINDER:
                if task_list.active_poll_id:
                    try:
                        await self.scheduler.poll_service.close_poll(task_list)
                    except Exception:
                        pass  # чтобы не падал use case

                task_list.active_poll_id = None
                task_list.poll_voted = False

        if week_days is not None:
            task_list.week_days = week_days

        # Сохраняем изменения
        self.user_service.save_user(user_id)

        # Синхронизируем с scheduler
        if task_list.is_valid_reminder():
            self.scheduler.upsert_list_jobs(task_list)
        else:
            # если напоминание отключено или некорректно — удаляем job
            self.scheduler.remove_list_jobs(user_id, list_id)

        return task_list