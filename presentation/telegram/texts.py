from aiogram.types import Message


def say_hello(username):
    return f"Привет {username}!\nЯ бот для ведения списков задач."



def get_main_menu_text():
    return "Главное меню:"
# /create_list_of_tasks 1 — Создать новый список задач
# /create_task 2 — Создать задачу
# /show_lists_of_tasks 3 — Показать списки
# /show_tasks 4 — Показать задачи
# q — Выйти""")
#    return text


def get_list_selection_text():
    return "Выберите список \nВведите номер (ID) этого списка:"

def get_list_created_text(list_of_tasks):
    return f"✅ Список '{list_of_tasks.title}' создан"

def get_no_lists_text():
    return "У вас еще нет списков"

def get_lists_text():
    return "Ваши списки:\n"


def get_list_selected_text(raw: int):
    return f"✅ Вы выбрали список с ID: {raw}"

def get_no_tasks_text():
    return "В этом списке нет задач."

def get_tasks_text(list_title: str):
    return f"Задачи списка '{list_title}':"

def get_task_created_text(task):
    return f"✅ Задача создана: {task.id} — {task.value}"

class TelegramView:
    def __init__(self, message: Message):
        self.message = message

    async def show(self, text: str):
        await self.message.answer(text)

    async def error(self, e: Exception):
        await self.message.answer(f"❌ Ошибка: {e}")

    async def show_lists(self, lists):
        text = "📋 *Ваши списки:*\n\n"
        for l in lists:
            text += f"▪️ *{l.id}* — {l.title}\n"

        await self.message.answer(text, parse_mode="Markdown")
