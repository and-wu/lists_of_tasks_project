from application.user.create_user import UserService

print("Здравствуйте")
choose = input("1 - выбрать пользователя (введите 1)\n2 - зарегистрироваться (введите 2)\nвведите 1 или 2 - ... ")

class CLI:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self._current_user_id: int | None = None

        # Меню будет меняться в зависимости от того, авторизован пользователь или нет
        self.auth_actions: dict[str, tuple[str, Callable]] = {
            "1": ("Войти как существующий пользователь", self.login),
            "2": ("Зарегистрироваться", self.register),
            "q": ("Выйти из программы", self.quit),
        }

        self.main_actions: dict[str, tuple[str, Callable]] = {
            "1": ("Создать список задач", self.create_task_list),
            "2": ("Создать задачу", self.create_task),
            "3": ("Показать мои списки задач", self.show_task_lists),
            "4": ("Выйти из аккаунта", self.logout),
            "q": ("Выйти из программы", self.quit),
        }



# def my_cli():
#     print("Выберите пользователя")
#     users = service.repo.all()
#     if users:
#         for user in users:
#             print(f"{user.id} --- {user.username}")
#
#         user_id = input('введите число соответсвующее имени для выбора пользователя: ')
#
#         user = service.repo.get_by_id(user_id=int(user_id))
#         print(f"Приветсвуем вас {user.name}")
#     else:
#         print('Еще не зарегистрировался ни один пользователь')
#         choose = "2"
#
#
#
# if choose == "2":
#     name = input('введите ваше имя: ')
#     while True:
#         username = input('введите ваше username: ')
#
#         try:
#             user = service.create_user(name=name, username=username)
#             print("Пользователь успешно создан")
#             break
#         except ValueError as e:
#             print('Username уже существует, придумайте новый пожалуйста, а то мы не сможем вас зарегистрировать')
#
# print(f"Вы - {user}")