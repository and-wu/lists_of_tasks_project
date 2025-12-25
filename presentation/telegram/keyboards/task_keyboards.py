from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from domain.tasks import Task


def get_extra_task_buttons(list_id) -> list[list[InlineKeyboardButton]]:
    """Возвращает список строк дополнительных кнопок для клавиатуры задач."""
    return [
        [
            InlineKeyboardButton(
                text="➕ Добавить новую задачу",
                callback_data=f"task:create:{list_id}",
            ),
        ],
        [InlineKeyboardButton(text="⬅️ Назад к спискам", callback_data="lists:show")],
    ]


def extra_task_menu(list_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=get_extra_task_buttons(list_id))


def get_tasks_keyboard(tasks, list_id) -> InlineKeyboardMarkup:
    keyboard = []

    for task in tasks:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"✅ {task.value}" if task.completed else f"⬜️ {task.value}",
                    callback_data=f"task:select:{task.id}",
                ),
            ],
        )

    # добавляем дополнительные кнопки
    keyboard.extend(get_extra_task_buttons(list_id=list_id))

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_task_detail_keyboard(task: Task, list_id: int) -> InlineKeyboardMarkup:
    keyboard = []

    # 1️⃣ Кнопка с текстом задачи (можно сделать toggle completed)
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"✅ {task.value}" if task.completed else f"⬜️ {task.value}",
                callback_data=f"task:toggle:{task.id}",
            ),
        ],
    )

    # 2️⃣ Кнопка редактирования
    keyboard.append(
        [
            InlineKeyboardButton(
                text="✏️ Изменить текст задачи",
                callback_data=f"task:edit:{task.id}",
            ),
        ],
    )

    # 3️⃣ Удаление
    keyboard.append(
        [
            InlineKeyboardButton(
                text="🗑 Удалить задачу",
                callback_data=f"task:delete:{task.id}",
            ),
        ],
    )

    # 4️⃣ Назад к списку задач
    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ К списку задач",
                callback_data=f"tasks:back:{list_id}",
            ),
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_delete_task_keyboard(
    task_id: int,
    list_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"tasks:delete:yes:{task_id}:{list_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data=f"tasks:delete:no:{task_id}:{list_id}",
                ),
            ],
        ],
    )
