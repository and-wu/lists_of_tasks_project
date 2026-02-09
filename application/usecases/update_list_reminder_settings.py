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
        run_date: Optional[datetime] = None,
        notification_type: NotificationType | None = None
    ) -> ListOfTasks:
        # Получаем список
        task_list = self.user_service.get_list_by_id(user_id, list_id)

        if task_list is None:
            raise ValueError(f"Список с id={list_id} не найден у пользователя {user_id}")

        # Обновляем напоминание
        if remind_time is not None:
            task_list.remind_time = remind_time

        if repeat_type is not None:
            task_list.repeat_type = repeat_type

        if run_date is not None:
            task_list.run_date = run_date

        if notification_type is not None:
            task_list.notification_type = notification_type

        # Сохраняем изменения
        self.user_service.save_user(user_id)

        # Синхронизируем с scheduler
        if task_list.is_valid_reminder():
            self.scheduler.upsert_list_jobs(task_list)
        else:
            # если напоминание отключено или некорректно — удаляем job
            self.scheduler.remove_list_jobs(user_id, list_id)

        return task_list