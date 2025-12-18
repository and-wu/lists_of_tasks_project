from aiogram.types import Message
from dataclasses import dataclass

from domain.tasks import Task


class BotMessages:
    """Общие тексты бота."""

    main_menu: str = "Главное меню:"

    @staticmethod
    def say_hello(username: str) -> str:
        return f"Привет {username}!\nЯ бот для ведения списков задач."


@dataclass
class ListView:
    """Тексты, связанные со списками задач."""

    main_menu: str = "Главное меню:"
    no_lists: str = "У вас еще нет списков"
    lists_text_header: str = "Ваши списки:\n"
    list_name_prompt: str = "Введите название для списка"
    list_name_empty: str = "Название не может быть пустым.\n Попробуйте снова:"
    list_delete_choice_prompt: str = "Выберите список для удаления:"
    list_deleted_success: str = "Список удалён ✅\n\n"
    action_canceled: str = "Действие отменено"
    delete_action_canceled: str = "Удаление отменено"

    def list_created(self, list_title: str) -> str:
        return f"✅ Список '{list_title}' успешно создан"

    def list_selected(self, list_id: int) -> str:
        return f"✅ Вы выбрали список с ID: {list_id}"

    @staticmethod
    def confirm_delete_list(title: str) -> str:
        return f"❗ Точно удалить список «{title}»?"

    def lists_text(self) -> str:
        return self.lists_text_header

@dataclass
class TaskView:
    """Тексты, связанные с задачами."""

    task_name_prompt: str = "Введите текст для задачи"
    task_name_empty: str = "Текст задачи не может быть пустым.\n Попробуйте снова:"
    list_not_found_error: str = "Список не найден"
    status_updated_success: str = "Статус обновлён"
    task_delete_success: str = "🗑 Задача удалена\n\n"
    action_canceled: str = "Действие отменено"
    delete_action_canceled: str = "Удаление отменено"

    def no_tasks_in_list(self, list_title: str) -> str:
        return f"В списке '{list_title}' нет задач."

    def task_created(self, task: Task) -> str:
        return f"✅ Задача создана: id = {task.id} — {task.value}"

    def get_list_title(self, list_title: str) -> str:
        return f"{list_title}"

    def task_text(self, task: Task) -> str:
        return f"📌 Задача:\n\n{task.value}"

    def task_updated_success(self, task: Task) -> str:
        return f"✅ Задача обновлена:\n\n{task.value}"

    def confirm_delete_task(self, task_value: str) -> str:
        return f"❗ Точно удалить задачу?\n\n«{task_value}»"








#def say_hello(username) -> str:
#    return f"Привет {username}!\nЯ бот для ведения списков задач."

#def get_main_menu_text() -> str:
#    return "Главное меню:"

#def get_list_selection_text() -> str:
#    return "Выберите список \nВведите номер (ID) этого списка:"

#def get_list_created_text(list_title) -> str:
#    return f"✅ Список '{list_title}' успешно создан"

#def get_no_lists_text() -> str:
#    return "У вас еще нет списков"

#def get_lists_text() -> str:
#    return "Ваши списки:\n"

#def get_list_name_prompt() -> str:
#    return "Введите название для списка"

#def get_list_name_empty_text() -> str:
#    return "Название не может быть пустым. Попробуйте снова:"

#def get_list_selected_text(raw: int) -> str:
#    return f"✅ Вы выбрали список с ID: {raw}"

#def get_no_tasks_text(list_title: str) -> str:
#    return f"В списке '{list_title}' нет задач."

#def get_tasks_text(list_title: str) -> str:
#    return f"{list_title}"

#def get_task_name_prompt() -> str:
#    return "Введите текст для задачи"

#def get_task_name_empty_text() -> str:
#    return "Текст задачи не может быть пустым. Попробуйте снова:"

#def get_task_created_text(task) -> str:
#    return f"✅ Задача создана: id = {task.id} — {task.value}"

#def get_action_canceled_text() -> str:
#    return "Действие отменено"