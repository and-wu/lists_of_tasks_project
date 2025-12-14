from aiogram.types import Message


def say_hello(username):
    return f"Привет {username}!\nЯ бот для ведения списков задач."



def main_menu():
    text = ("""Главное меню:
/create_list_of_tasks 1 — Создать новый список задач
/create_task 2 — Создать задачу
/show_lists_of_tasks 3 — Показать списки
/show_tasks 4 — Показать задачи
q — Выйти""")

    return text


def get_list_id():
    return "Выберите список \nВведите номер (ID) этого списка:"

def successful_list_create_text(list_of_tasks):
    return f"✅ Список '{list_of_tasks.title}' создан"

def not_lists_user():
    return "У вас еще нет списков"

def show_lists_of_tasks(lists):
    text = "Ваши списки:\n"
    for l in lists:
        text += f"{l.id} список — {l.title}\n"
    return text

def successful_choice_list(raw: int):
    return f"✅ Вы выбрали список с ID: {raw}"

def not_tasks_text():
    return "В этом списке нет задач."

def show_tasks(tasks):
    text = "Задачи списка:\n"
    for task in tasks:
        text += f"Задача {task.id}: {task.value}: статус - {task.completed}\n"
    return text

def successful_task_create(task):
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
