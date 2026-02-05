from datetime import time, datetime
from typing import Optional

from domain.task_list import ListOfTasks, RepeatType
from application.user.create_user import UserService


class CreateListUseCase:
    """
    Use case для создания нового списка задач.
    Можно сразу указать напоминание или оставить пустым.
    """

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(
            self,
            user_id: int,
            title: str,
            *,
            remind_time: Optional[time] = None,
            repeat_type: Optional[RepeatType] = None,
            run_date: Optional[datetime] = None,
    ) -> ListOfTasks:
        """
        Создаёт новый список задач для пользователя.

        :param user_id: ID пользователя
        :param title: название нового списка
        :param remind_time: время уведомления (опционально)
        :param repeat_type: тип повторения уведомления (опционально)
        :param run_date: дата для одноразового уведомления (опционально)
        :return: объект ListOfTasks
        """
        # вызываем сервис пользователя для создания списка
        new_list = self.user_service.add_list_of_tasks(
            user_id=user_id,
            title=title,
            remind_time=remind_time
        )

        # если переданы repeat_type или run_date, сразу их устанавливаем
        if repeat_type:
            new_list.repeat_type = repeat_type
        if run_date:
            new_list.run_date = run_date

        # сохраняем изменения
        self.user_service.save_user(user_id)

        return new_list