
from domain.errors import (
    InvalidMenuChoiceError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)


class Controller:
    def __init__(self, user_service, view) -> None:
        self.user_service = user_service
        self.view = view
        self._current_user_id = None
        self.user = None
        self.running = True


    def run(self) -> None:
        while self.running:
            try:
                if not self._current_user_id:
                    self.auth_flow()
                else:
                    self.main_flow()
            except Exception as e:
                self.view.error(e)

    # ===== Поток для неавторизованного пользователя =====
    def auth_flow(self) -> None:
        self.view.auth_menu.show_auth_menu()
        choice = self.view.get_user_choice()

        if choice ==  "1":
            self.select()
        elif choice == "2":
            self.create_user()
        elif choice == "q":
            self.quit()
        else:
            raise InvalidMenuChoiceError



    def select(self) -> None:
        users = self.user_service.repo.all()

        if not users:
            self.view.not_users()
            return

        while True:
            self.view.show_users(users)
            raw_id = self.view.get_user_id()

            user = self.user_service.repo.get_by_id(user_id=int(raw_id))
            if user is None:
                raise UserNotFoundError
            self.view.auth_menu.hello(user)
            self._current_user_id = user.id
            self.user = user
            break


    def create_user(self) -> None:
        name = self.view.get_user_name()
        while True:
            username = self.view.get_user_username()

            try:
                user = self.user_service.create_user(name=name, username=username)
                self._current_user_id = user.id
                self.user = user
                self.view.auth_menu.successful_user_create_text(self.user)
                break
            except UsernameAlreadyExistsError as e:
                self.view.error(e)


    def quit(self) -> None:
        self.view.auth_menu.quit()
        self._running = False

    # ===== Поток для авторизованного пользователя =====
    def main_flow(self) -> None:
        self.view.main_menu.show_main_menu()
        choice = self.view.get_user_choice()

        if choice == "1":
            self.create_lists_of_tasks()
        elif choice == "2":
            self.create_task()
        elif choice == "3":
            self.show_lists_of_tasks()
        elif choice == "4":
            self.show_tasks()
        elif choice == "q":
            self.logout()
        elif choice == "l":
            self.quit()
        else:
            raise InvalidMenuChoiceError

    def create_lists_of_tasks(self) -> None:
        self.view.main_menu.create_list_text()
        title = self.view.get_list_name()
        list_of_tasks = self.user_service.add_list_of_tasks(user_id=self._current_user_id, title=title)
        self.view.main_menu.get_list_created_text(list_of_tasks=list_of_tasks)

        while True:
            self.view.main_menu.show_mini_menu()
            choice = self.view.get_user_choice()
            if choice == "1":
                self.add_task_to_specific_list(list_of_tasks.id)
            elif choice == "2":
                return
            else:
                try:
                    raise InvalidMenuChoiceError
                except InvalidMenuChoiceError as e:
                    self.view.error(e)

    def add_task_to_specific_list(self, list_id: int):
        value = self.view.get_task_text()

        task = self.user_service.add_task(
            user_id=self._current_user_id,
            list_id=list_id,
            value=value,
        )

        self.view.main_menu.get_task_created_text(task)

        return task

    def create_task(self) -> None:
        self.view.main_menu.create_task_text()
        list_id = int(self.select_list_of_tasks())

        self.add_task_to_specific_list(list_id)

        # Мини-меню после создания и добавления задачи
        while True:

            choice = self.view.get_user_choice()

            if choice == "1":
                self.add_task_to_specific_list(list_id)

            elif choice == "2":
                break
            else:
                raise InvalidMenuChoiceError

    def show_lists_of_tasks(self) -> None:
        if not self.user.listoftasks:
            self.view.main_menu.get_no_lists_text()
        self.view.show_lists(self.user.listoftasks)

    def show_tasks(self) -> None:
        list_id = self.select_list_of_tasks()

        tasks = self.user_service.get_tasks(self._current_user_id, list_id)

        if not tasks:
            self.view.main_menu.get_no_tasks_text()
            return

        self.view.get_tasks_text(tasks)

    def select_list_of_tasks(self) -> int | None:
        while True:
            self.view.show_lists(self.user.listoftasks)
            raw = self.view.get_list_selection_text()

            try:
                return int(raw)
            except ValueError as e:
                self.view.error(e)


    def logout(self) -> None:
        self.view.main_menu.logout()
        self._current_user_id = None
        self.user = None


