from datetime import time

from domain.errors import ListAlreadyExistsError
from domain.SQLite_models.tasks_list import ListOfTasks
from domain.SQLite_models.tasks import Task
from domain.SQLite_models.users import User
from domain.interfaces.user_repository import IUserRepository

class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    def create_user(self, user_id, name, username) -> User:
        # Проверки
        if self.repo.get_by_id(user_id):
            raise ValueError("User already exists")

        user = User(
            id=user_id,
            name=name,
            username=username
        )

        self.repo.save(user)
        return user

    def get_or_create_user(self, user_id: int, name: str, username: str | None) -> User:
        user = self.repo.get_by_id(user_id)
        if user:
            return user

        return self.create_user(user_id, name, username)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        return user


    def add_list_of_tasks(self, user_id: int, title, remind_time: None | time) -> ListOfTasks:
        user = self.repo.get_by_id(user_id)

        normalized_title = title.strip().lower()

        # ✅ Проверка на дубликат
        for list_tasks in user.listoftasks:
            if list_tasks.title.strip().lower() == normalized_title:
                raise ListAlreadyExistsError()

        # генерация id
        max_id = 0
        for list_tasks in user.listoftasks:
            max_id = max(list_tasks.id, max_id) + 1

        list_of_tasks = ListOfTasks(
            id=max_id,
            title=title,
            owner_id=user_id,
            remind_time=remind_time
        )

        user.listoftasks.append(list_of_tasks)
        self.repo.save(user)

        return list_of_tasks

    def _next_task_id(self, user: User) -> int:
        all_tasks = [
            task.id
            for task_list in user.listoftasks
            for task in task_list.tasks
        ]
        return max(all_tasks, default=-1) + 1

    def add_task(self, user_id: int, list_id: int, value) -> Task:
        user = self.repo.get_by_id(user_id)
        target_list = None
        for list_of_tasks in user.listoftasks:
            if list_of_tasks.id == list_id:
                target_list = list_of_tasks
                break
        if target_list is None:
            raise ValueError("нет такого списка")

        task = Task(id=self._next_task_id(user), value=value)

        target_list.add_task_to_list(task)

        self.repo.save(user)

        return task

    def get_tasks(self, user_id, list_of_tasks_id):
        user =  self.repo.get_by_id(user_id)

        for listoftasks in user.listoftasks:
            if listoftasks.id == list_of_tasks_id:
                return listoftasks.tasks


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

    def get_task_with_list(self, user_id: int, task_id: int) -> tuple[Task, int] | None:
        user = self.repo.get_by_id(user_id)

        for task_list in user.listoftasks:
            for task in task_list.tasks:
                if task.id == task_id:
                    return task, task_list.id

        return None

    def update_task_text(self, user_id: int, task_id: int, new_value: str):
        task = self.repo.update_task_text(user_id, task_id, new_value)

        if not task:
            raise ValueError("Task not found")

        return task

    def delete_list_of_tasks(self, user_id: int, list_id: int) -> bool:
        """
        Удаляет список и возвращает True, если успешно.
        """
        success = self.repo.delete_list(user_id, list_id)
        return success

    def delete_task(self, user_id: int, task_id: int) -> bool:
        """
        Удаляет задачу и возвращает True, если успешно.
        """
        success = self.repo.delete_task(user_id, task_id)
        return success

    def save_user(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        self.repo.save(user)

    def toggle_task_completed(self, user_id: int, task_id: int):
        """
        Переключает статус выполнения задачи (completed / not completed)
        """
        user = self.repo.get_by_id(user_id)

        for task_list in user.listoftasks:
            for task in task_list.tasks:
                if task.id == task_id:
                    task.completed = not task.completed
                    self.save_user(user_id)
                    return task

        raise ValueError(f"Task with id={task_id} not found")

    def reset_all_tasks(self) -> dict[int, list[dict]]:
        return self.repo.reset_all_tasks()

    def set_google_sheet(self, user_id: int, sheet_url: str):
        user = self.repo.get_by_id(user_id)
        user.google_sheet_url = sheet_url
        self.repo.save(user)

    def get_all_users(self) -> list[User]:
        """
        Возвращает список всех пользователей из репозитория.
        """
        return self.repo.all()

    def update_list_remind_time(self, user_id: int, list_id: int, new_time: time):
        user = self.get_user_by_id(user_id)

        for task_list in user.listoftasks:
            if task_list.id == list_id:
                task_list.remind_time = new_time
                break

        self.save_user(user_id)