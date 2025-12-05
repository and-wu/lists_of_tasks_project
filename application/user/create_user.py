from domain.task_list import ListOfTasks
from domain.tasks import Task
from domain.users import User
from domain.interfaces.user_repository import IUserRepository


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    def create_user(self, name, username) -> User:
        # Проверки
        if self.repo.get_by_username(username):
            raise ValueError("Username already exists")

        user = User(id=0, name=name, username=username)
        self.repo.save(user)

        return User(id=user.id, name=user.name, username=user.username)


    def add_list_of_tasks(self, user_id: int, title) -> ListOfTasks:
        user = self.repo.get_by_id(user_id)
        max_id = 0
        for list_tasks in user.listoftasks:
            max_id = max(list_tasks.id, max_id) + 1

        list_of_tasks = ListOfTasks(max_id, title, user_id)
        user.listoftasks.append(list_of_tasks)

        self.repo.save(user)

        return list_of_tasks

    def add_task(self, user_id: int, list_id, value) -> Task:
        user = self.repo.get_by_id(user_id)
        target_list = None
        for list_of_tasks in user.listoftasks:
            if list_of_tasks.id == list_id:
                target_list = list_of_tasks
                break
        if target_list is None:
            raise ValueError("нет такого списка")

        task = Task(id=target_list.max_id(), value=value)

        target_list.add_task_to_list(task)

        self.repo.save(user)

        return task



