from datetime import datetime
from typing import Iterable

from application.scheduler.reminder_scheduler import ReminderScheduler
from application.user.create_user import UserService
from domain.enums.repeat_type import RepeatType
from domain.task_list import ListOfTasks


class SyncListReminderWithSchedulerUseCase:
    """
    Use case для синхронизации напоминаний списков с scheduler.

    Используется:
    - при старте приложения
    - при восстановлении scheduler
    - потенциально при миграциях / реиндексации job'ов

    Источник истины — ListOfTasks.
    Scheduler приводится в соответствие с текущим состоянием домена.
    """

    def __init__(
        self,
        user_service: UserService,
        scheduler: ReminderScheduler,
    ):
        self.user_service = user_service
        self.scheduler = scheduler

    def execute(self) -> None:
        """
        Синхронизирует ВСЕ списки ВСЕХ пользователей с scheduler.
        """
        users = self.user_service.get_all_users()

        for user in users:
            self._sync_user_lists(user.listoftasks)

    # -------------------------
    # Internal
    # -------------------------

    def _sync_user_lists(self, lists: Iterable[ListOfTasks]) -> None:
        for task_list in lists:

            # ❌ напоминание выключено или некорректно
            if not task_list.is_valid_reminder():
                self.scheduler.remove_list_jobs(
                    user_id=task_list.owner_id,
                    list_id=task_list.id,
                )
                continue

            # ❌ одноразовое напоминание уже в прошлом
            if self._is_expired_once(task_list):
                self.scheduler.remove_list_jobs(
                    user_id=task_list.owner_id,
                    list_id=task_list.id,
                )
                continue

            # ✅ валидное активное напоминание
            self.scheduler.upsert_list_jobs(task_list)

    @staticmethod
    def _is_expired_once(task_list: ListOfTasks) -> bool:
        return (
            task_list.repeat_type == RepeatType.ONCE
            and task_list.run_date is not None
            and task_list.run_date < datetime.now()
        )