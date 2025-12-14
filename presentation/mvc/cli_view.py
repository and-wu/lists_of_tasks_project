
class AuthMenuView:
    """Отображение меню и сообщений авторизации"""

    def show_auth_menu(self):
        print("1: Войти как существующий пользователь")
        print("2: Зарегистрироваться")
        print("q: Выйти из программы")

    def not_users(self):
        print("Еще нет ни одного пользователя")

    def hello(self, user):
        print(f"Приветсвуем вас {user.name}")

    def successful_user_create_text(self, user):
        print(f"Пользователь {user.name} успешно создан")
        print(f"Вы - {user}\nВаш user_id = {user.id}")

    def quit(self):
        print("Выход из программы. До свидания!")


class MainMenuView:
    """Отображение главного меню и действий с задачами"""

    def show_main_menu(self):
        print("1: Создать список задач")
        print("2: Создать задачу")
        print("3: Показать мои списки задач")
        print("4: Посмотреть задачи в списке")
        print("q: Выйти из аккаунта")
        print("l: Выйти из программы")

    def show_mini_menu(self):
        print("\nЧто дальше?")
        print("1: Добавить задачу в этот список")
        print("2: Вернуться в главное меню")

    def create_list_text(self):
        print("Создания списка")

    def successful_list_create_text(self, list_of_tasks):
        print(f"✅ Список '{list_of_tasks.title}' создан")

    def create_task_text(self):
        print("**Создание задачи**, вот ваши списки:")

    def successful_task_create(self, task):
        print(f"✅ Задача создана: {task.id} — {task.value}")

    def not_tasks_text(self):
        print("В этом списке нет задач.")

    def not_lists_user(self):
        print("У вас еще нет списков")

    def logout(self):
        print("Выход из аккаунта. До свидания!")


class CLIView:
    """Базовый класс: общие методы ввода/вывода"""

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
    def show_users(self, users):
        for u in users:
            print(f"{u.id} — {u.username}")

    def show_lists(self, lists):
        print("Ваши списки:")
        for l in lists:
            print(f"{l.id} — {l.title}")
        print()

    def show_tasks(self, tasks):
        print("Задачи списка:")
        for task in tasks:
            print(f"Задача {task.id}: {task.value}: статус - {task.completed}")
        print()

    # ===== Текстовые сообщения =====
    def info(self, msg):
        print(msg)

    def error(self, error: Exception):
        print(error)
