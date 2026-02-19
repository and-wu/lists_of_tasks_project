from datetime import time

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from domain.tasks import Task

def remind_manage_keyboard_with_time(list_id: int, remind_time: time) -> InlineKeyboardMarkup:
    """
    Если время УЖЕ есть
    """
    time_str = remind_time.strftime("%H:%M")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✏️ Изменить время ({time_str})",
                    callback_data=f"list:remind_edit:{list_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить время",
                    callback_data=f"list:remind_remove:{list_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отменить и вернуться к списку",
                    callback_data=f"list:remind_cancel:{list_id}"
                )
            ]
        ]
    )


def remind_manage_keyboard_without_time(list_id: int) -> InlineKeyboardMarkup:
    """
    Если времени ЕЩЁ нет
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕⏰ Установить время",
                    callback_data=f"list:remind_add:{list_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отменить и вернуться к списку",
                    callback_data=f"list:remind_cancel:{list_id}"
                )
            ]
        ]
    )
def get_extra_task_buttons(list_id) -> list[list[InlineKeyboardButton]]:
    """
    Возвращает список строк дополнительных кнопок для клавиатуры задач
    """
    return [
        [InlineKeyboardButton(text="➕ Добавить новую задачу", callback_data=f"task:create:{list_id}")],
        [InlineKeyboardButton(
                text="⏰ Редактировать время напоминания",
                callback_data=f"list:remind_menu:{list_id}"
            )],
        [InlineKeyboardButton(
                text="🗓 Изменить периодичность",
                callback_data=f"edit_repeat:{list_id}"
            )],
        [InlineKeyboardButton(
                text="🔄 Сменить тип уведомления",
                callback_data=f"toggle_notification:{list_id}"
            )],
        [InlineKeyboardButton(text="⬅️ Назад к спискам", callback_data="lists:show")]
    ]

def extra_task_menu(list_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=get_extra_task_buttons(list_id))

def get_tasks_keyboard(tasks, list_id, tasks_list=None) -> InlineKeyboardMarkup:
    keyboard = []

    for task in tasks:
        keyboard.append([
            InlineKeyboardButton(
                text=f"✅ {task.value}" if task.completed else f"⬜️ {task.value}",
                callback_data=f"task:select:{task.id}"
            )
        ])

    # добавляем дополнительные кнопки
    keyboard.extend(get_extra_task_buttons(list_id=list_id))


    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def get_task_detail_keyboard(task: Task, list_id: int) -> InlineKeyboardMarkup:
    keyboard = []

    # 1️⃣ Кнопка с текстом задачи (можно сделать toggle completed)
    keyboard.append([
        InlineKeyboardButton(
            text=f"✅ {task.value}" if task.completed else f"⬜️ {task.value}",
            callback_data=f"task:toggle:{task.id}"
        )
    ])

    # 2️⃣ Кнопка редактирования
    keyboard.append([
        InlineKeyboardButton(
            text="✏️ Изменить текст задачи",
            callback_data=f"task:edit:{task.id}"
        )
    ])

    # 3️⃣ Удаление
    keyboard.append([
        InlineKeyboardButton(
            text="🗑 Удалить задачу",
            callback_data=f"task:delete:{task.id}"
        )
    ])

    # 4️⃣  Назад к списку задач
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ К списку задач",
            callback_data=f"tasks:back:{list_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_delete_task_keyboard(task_id: int, list_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"tasks:delete:yes:{task_id}:{list_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data=f"tasks:delete:no:{task_id}:{list_id}"
                )
            ]
        ]
    )

