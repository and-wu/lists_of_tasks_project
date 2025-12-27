
class AuthMenuView:
    """Отображение меню и сообщений авторизации."""

    def show_auth_menu(self) -> None:
        pass

    def not_users(self) -> None:
        pass

    def hello(self, user) -> None:
        pass

    def successful_user_create_text(self, user) -> None:
        pass

    def quit(self) -> None:
        pass


class MainMenuView:
    """Отображение главного меню и действий с задачами."""

    def show_main_menu(self) -> None:
        pass

    def show_mini_menu(self) -> None:
        pass

    def create_list_text(self) -> None:
        pass

    def successful_list_create_text(self, list_of_tasks) -> None:
        pass

    def create_task_text(self) -> None:
        pass

    def successful_task_create(self, task) -> None:
        pass

    def not_tasks_text(self) -> None:
        pass

    def not_lists_user(self) -> None:
        pass

    def logout(self) -> None:
        pass


class CLIView:
    """Базовый класс: общие методы ввода/вывода."""

    main_menu = MainMenuView()
    auth_menu = AuthMenuView()

    # ===== Ввод пользователя =====
    def get_user_id(self):
        return input("Введите номер пользователя: ")

    def get_user_name(self):
        return input("Введите ваше имя: ")

    def get_user_username(self):
        return input("Введите ваш username: ")

    def get_user_choice(self):
        return input("\nВыберите действие: ")

    def get_list_name(self):
        return input("\nВведите название для списка: ")

    def get_list_id(self):
        return input("Выберите список \nВведите номер этого списка: ")

    def get_task_text(self):
        return input("Введите текст задачи: ")

    def get_task_id_to_delete(self):
        return input("Введите номер задачи для удаления: ")


    # ===== Общий вывод =====
    def show_users(self, users) -> None:
        for _u in users:
            pass

    def show_lists(self, lists) -> None:
        for _l in lists:
            pass

    def show_tasks(self, tasks) -> None:
        for _task in tasks:
            pass

    # ===== Текстовые сообщения =====
    def info(self, msg) -> None:
        pass

    def error(self, error: Exception) -> None:
        pass
