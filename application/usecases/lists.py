from datetime import time

from application.scheduler.reminder_scheduler import ReminderScheduler
from application.user.create_user import UserService
from domain.task_list import ListOfTasks


class CreateNewListUseCase:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, user_id: int, list_title: str) -> ListOfTasks:
        return self.user_service.add_list_of_tasks(user_id, list_title, remind_time=None)


class AddRemindTimeUseCase:
    def __init__(self, scheduler: ReminderScheduler):
        self.scheduler = scheduler

    async def execute(self, user_id: int, list_id: int, remind_time: time) -> None:
        self.scheduler.schedule_list_reminder(
            user_id=user_id,
            list_id=list_id,
            remind_time=remind_time,
        )


class CreateDailyPollUseCase:
    def __init__(self, scheduler: ReminderScheduler):
        self.scheduler = scheduler

    async def execute(self, user_id: int, list_id: int, remind_time: time):
        """Регистрируем ежедневный опрос для конкретного списка"""
        self.scheduler.schedule_poll_for_list(
            user_id=user_id,
            list_id=list_id,
            remind_time=remind_time,
        )

class UpdateRemindTimeUseCase:
    def __init__(
        self,
        user_service: UserService,
        scheduler: ReminderScheduler,
    ):
        self.user_service = user_service
        self.scheduler = scheduler

    async def execute(self, user_id: int, list_id: int, new_time: time):
        # 💾 сохраняем в данных
        self.user_service.update_list_remind_time(
            user_id=user_id,
            list_id=list_id,
            new_time=new_time,
        )

        # ⏰ обновляем job
        self.scheduler.update_list_remind_time(
            user_id=user_id,
            list_id=list_id,
            new_time=new_time,
        )