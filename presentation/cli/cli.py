from typing import Callable

from application.user.create_user import UserService

print("Здравствуйте")

class CLI:
    def __init__(self, user_service: UserService):
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


    def run(self):
        while self._running:
            # Выбираем правильное меню
            if self._current_user_id is None:
                menu = self.auth_actions
                title = "Меню авторизации"
            else:
                menu = self.main_actions
                title = "Главное меню"

            print(f"\n==== {title} ====")
            for key, (value, func) in menu.items():
                print(f"{key}: {value}")

            choice = input("Выберите действие: ")

            action = menu.get(choice)

            if action is None:
                print("Неверный пункт меню, попробуйте снова")
                continue

            _, func = action
            try:
                func()   # вызываем метод класса CLI
            except Exception as e:
                print(f"❌ Ошибка: {e}")



    def select(self):
        print("Выберите пользователя")
        users = self.user_service.repo.all()

        if not users:
            print("Еще нет ни одного пользователя")

        while True:
            if users:
                for user in users:
                    print(f"{user.id} --- {user.username}")
                user_id = input('введите число соответсвующее имени для выбора пользователя: ').strip()

                try:
                    user = self.user_service.repo.get_by_id(user_id=int(user_id))
                    if user is None:
                        raise ValueError("Пользователь с таким ID не найден")
                    print(f"Приветсвуем вас {user.name}")
                    self._current_user_id = user.id
                    self.user = user
                    break
                except Exception as e:
                    print(f"Ошибка: {e}. Попробуйте снова.")


    def creat(self):
        print("register there")
        name = input('введите ваше имя: ')
        while True:
            username = input('введите ваше username: ')

            try:
                user = self.user_service.create_user(name=name, username=username)
                self._current_user_id = user.id
                self.user = user
                print("Пользователь успешно создан")
                break
            except ValueError as e:
                print('Username уже существует, придумайте новый пожалуйста, а то мы не сможем вас добавить')

        print(f"Вы - {user}\nВаш user_id = {self._current_user_id}")

    def quit(self):
        print("Выход из программы. До свидания!")
        self._running = False

    def create_lists_of_tasks(self):
        print("Создания списка")
        title = input('Введите название для списка задач - ')
        list_of_tasks = self.user_service.add_list_of_tasks(user_id=self._current_user_id, title=title)
        print(print(f"✅ Список '{list_of_tasks.title}' создан"))

        # Мини-меню после создания списка
        while True:
            print("\nЧто дальше?")
            print("1 — Добавить задачу в этот список")
            print("2 — Вернуться в главное меню")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.add_task_to_specific_list(list_of_tasks.id)

            elif choice == "2":
                break
            else:
                print("❌ Неверный ввод, попробуйте снова")



    def add_task_to_specific_list(self, list_id: int):
        value = input("Введите текст задачи: ")

        task = self.user_service.add_task(
            user_id=self._current_user_id,
            list_id=list_id,
            value=value
        )

        print(f"✅ Задача создана: {task.id} — {task.value}")


    def create_task(self):
        print("Создание задачи. Выбери список в который нужно добавить задачу")
        list_id = int(self.select_list_of_tasks())
        self.add_task_to_specific_list(list_id)

        # Мини-меню после создания и добавления задачи
        while True:
            print("\nЧто дальше?")
            print("1 — Добавить еще задачу в этот список")
            print("2 — Вернуться в главное меню")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.add_task_to_specific_list(list_id)

            elif choice == "2":
                break
            else:
                print("❌ Неверный ввод, попробуйте снова")

    def show_lists_of_tasks(self):
        # Просмотр списков пользователя
        # user = self.user_service.get_user_by_id(user_id=self._current_user_id)

        for list_tasks in self.user.listoftasks:
            print(f"{list_tasks.id} - {list_tasks.title}")

    def select_list_of_tasks(self) -> int | None:
        while True:
            print("Выбор списка")
            self.show_lists_of_tasks()
            raw = input('Введите номер списка задач - ')

            if raw.lower() == "q":
                return None

            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите число")

    def display_tasks(self, tasks):
        if not tasks:
            print("В этом списке нет задач.")
            return

        for task in tasks:
            print(f"Задача {task.id}: {task.value}: статус - {task.completed}")

    def show_tasks(self):
        list_id = self.select_list_of_tasks()

        tasks = self.user_service.get_tasks(self._current_user_id, list_id)

        self.display_tasks(tasks)


    def logout(self):
        print("Вы вышли из аккаунта.")
        self._current_user_id = None



