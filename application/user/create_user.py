from datetime import time

from domain.interfaces.user_repository import IUserRepository
from domain.task_list import ListOfTasks
from domain.tasks import Task
from domain.users import User


class UserService:
    def __init__(self, repo: IUserRepository) -> None:
        self.repo = repo

    def create_user(self, user_id: int, name: str, username: str | None) -> User:
        if self.repo.get_by_username(username):
            msg = "Username already exists"
            raise ValueError(msg)

        user = User(id=user_id, name=name, username=username)
        self.repo.save(user)

        return User(id=user_id, name=user.name, username=user.username)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            msg = "Пользователь не найден"
            raise ValueError(msg)
        return user

    def add_list_of_tasks(
        self, user_id: int, title: str, remind_time: None | time
    ) -> ListOfTasks:
        user = self.repo.get_by_id(user_id)
        max_id = 0
        for list_tasks in user.listoftasks:
            max_id = max(list_tasks.id, max_id) + 1

        list_of_tasks = ListOfTasks(
            id=max_id, title=title, owner_id=user_id, remind_time=remind_time
        )
        user.listoftasks.append(list_of_tasks)

        self.repo.save(user)

        return list_of_tasks

    def _next_task_id(self, user: User) -> int:
        all_tasks = [
            task.id for task_list in user.listoftasks for task in task_list.tasks
        ]
        return max(all_tasks, default=-1) + 1

    def add_task(self, user_id: int, list_id: int, value: str) -> Task:
        user = self.repo.get_by_id(user_id)
        target_list = None
        for list_of_tasks in user.listoftasks:
            if list_of_tasks.id == list_id:
                target_list = list_of_tasks
                break
        if target_list is None:
            msg = "нет такого списка"
            raise ValueError(msg)

        task = Task(id=self._next_task_id(user), value=value)

        target_list.add_task_to_list(task)

        self.repo.save(user)

        return task

    def get_tasks(self, user_id: str | int, list_of_tasks_id: int):
        user = self.repo.get_by_id(user_id)

        for listoftasks in user.listoftasks:
            if listoftasks.id == list_of_tasks_id:
                return listoftasks.tasks
        return None

    def show_lists_of_tasks(self, user_id: int) -> list:
        user_lists = []
        user = self.repo.get_by_id(user_id)
        for listoftasks in user.listoftasks:
            user_lists.append((listoftasks.id, listoftasks.title))
        return user_lists

    def get_list_by_id(self, user_id: int, list_id: int) -> ListOfTasks | None:
        user = self.repo.get_by_id(user_id)

        for listoftasks in user.listoftasks:
            if listoftasks.id == list_id:
                return listoftasks
        return None

    def get_task_with_list(self, user_id: int, task_id: int) -> tuple[Task, int] | None:
        user = self.repo.get_by_id(user_id)

        for task_list in user.listoftasks:
            for task in task_list.tasks:
                if task.id == task_id:
                    return task, task_list.id

        return None

    def update_task_text(self, user_id: int, task_id: int, new_value: str) -> Task:
        task, _ = self.get_task_with_list(user_id, task_id)
        task.value = new_value
        self.repo.save(self.repo.get_by_id(user_id))
        return task

    def delete_list_of_tasks(self, user_id: int, list_id: int) -> bool:
        """Удаляет список и возвращает True, если успешно."""
        return self.repo.delete_list(user_id, list_id)

    def delete_task(self, user_id: int, task_id: int) -> bool:
        """Удаляет задачу и возвращает True, если успешно."""
        return self.repo.delete_task(user_id, task_id)

    def save_user(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        self.repo.save(user)

    def toggle_task_completed(self, user_id: int, task_id: int) -> Task | None:
        """Переключает статус выполнения задачи (completed / not completed)."""
        user = self.repo.get_by_id(user_id)

        for task_list in user.listoftasks:
            for task in task_list.tasks:
                if task.id == task_id:
                    task.completed = not task.completed
                    self.save_user(user_id)
                    return task

        msg = f"Task with id={task_id} not found"
        raise ValueError(msg)
