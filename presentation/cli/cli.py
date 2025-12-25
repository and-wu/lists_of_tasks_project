
from typing import TYPE_CHECKING

from application.user.create_user import UserService

if TYPE_CHECKING:
    from collections.abc import Callable


class CLI:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service
        self._current_user_id: int | None = None
        self.user = None
        self._running = True

        # Меню будет меняться в зависимости от того, авторизован пользователь или нет
        self.auth_actions: dict[str, tuple[str, Callable]] = {
            "1": ("Войти как существующий пользователь", self.select),
            "2": ("Зарегистрироваться", self.creat),
            "q": ("Выйти из программы", self.quit),
        }

        self.main_actions: dict[str, tuple[str, Callable]] = {
            "1": ("Создать список задач", self.create_lists_of_tasks),
            "2": ("Создать задачу", self.create_task),
            "3": ("Показать мои списки задач", self.show_lists_of_tasks),
            "4": ("Посмотреть задачи в списке", self.show_tasks),
            "5": ("Выйти из аккаунта", self.logout),
            "q": ("Выйти из программы", self.quit),
        }


    def run(self) -> None:
        while self._running:
            # Выбираем правильное меню
            if self._current_user_id is None:
                menu = self.auth_actions
            else:
                menu = self.main_actions

            for (_value, func) in menu.values():
                pass

            choice = input("Выберите действие: ")

            action = menu.get(choice)

            if action is None:
                continue

            _, func = action
            try:
                func()   # вызываем метод класса CLI
            except Exception:
                pass



    def select(self) -> None:
        users = self.user_service.repo.all()

        if not users:
            pass

        while True:
            if users:
                for user in users:
                    pass
                user_id = input("введите число соответсвующее имени для выбора пользователя: ").strip()

                try:
                    user = self.user_service.repo.get_by_id(user_id=int(user_id))
                    if user is None:
                        msg = "Пользователь с таким ID не найден"
                        raise ValueError(msg)
                    self._current_user_id = user.id
                    self.user = user
                    break
                except Exception:
                    pass


    def creat(self) -> None:
        name = input("введите ваше имя: ")
        while True:
            username = input("введите ваше username: ")

            try:
                user = self.user_service.create_user(name=name, username=username)
                self._current_user_id = user.id
                self.user = user
                break
            except ValueError:
                pass


    def quit(self) -> None:
        self._running = False

    def create_lists_of_tasks(self) -> None:
        title = input("Введите название для списка задач - ")
        list_of_tasks = self.user_service.add_list_of_tasks(user_id=self._current_user_id, title=title)

        # Мини-меню после создания списка
        while True:

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.add_task_to_specific_list(list_of_tasks.id)

            elif choice == "2":
                break
            else:
                pass



    def add_task_to_specific_list(self, list_id: int) -> None:
        value = input("Введите текст задачи: ")

        self.user_service.add_task(
            user_id=self._current_user_id,
            list_id=list_id,
            value=value,
        )



    def create_task(self) -> None:
        list_id = int(self.select_list_of_tasks())
        self.add_task_to_specific_list(list_id)

        # Мини-меню после создания и добавления задачи
        while True:

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.add_task_to_specific_list(list_id)

            elif choice == "2":
                break
            else:
                pass

    def show_lists_of_tasks(self) -> None:

        for _list_tasks in self.user.listoftasks:
            pass

    def select_list_of_tasks(self) -> int | None:
        while True:
            self.show_lists_of_tasks()
            raw = input("Введите номер списка задач - ")

            if raw.lower() == "q":
                return None

            try:
                return int(raw)
            except ValueError:
                pass

    def display_tasks(self, tasks) -> None:
        if not tasks:
            return

        for _task in tasks:
            pass

    def show_tasks(self) -> None:
        list_id = self.select_list_of_tasks()

        tasks = self.user_service.get_tasks(self._current_user_id, list_id)

        self.display_tasks(tasks)


    def logout(self) -> None:
        self._current_user_id = None



