from dataclasses import dataclass

from domain.tasks import Task


class BotMessages:
    """Общие тексты бота."""

    main_menu: str = "Главное меню:"

    @staticmethod
    def say_hello(username: str) -> str:
        return (f"Привет {username}!\nЯ бот для ведения списков задач."
                f"\nПосмотреть главное меню можно через команду /main_menu")


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

    def task_created(self, task: dict) -> str:
        return f"✅ Задача создана: id = {task["id"]} — {task["value"]}"

    def get_list_title(self, list_title: str) -> str:
        return f"Список - {list_title}"

    def task_text(self, task: Task) -> str:
        return f"📌 Задача:\n\n{task.value}"

    def task_updated_success(self, task: Task) -> str:
        return f"✅ Задача обновлена:\n\n{task.value}"

    def confirm_delete_task(self, task_value: str) -> str:
        return f"❗ Точно удалить задачу?\n\n«{task_value}»"

    def task_new_text_prompt(self, task):
        return (
        f"✏️ <b>Редактирование задачи</b>\n\n"
        f"<b>Текущий текст:</b>\n"
        f"<code>{task.value}</code>\n\n"
        f"Отправьте новый текст задачи:"
    )
