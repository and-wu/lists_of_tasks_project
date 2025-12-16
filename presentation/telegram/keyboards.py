from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Посмотреть списки",
                    callback_data="show_lists"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Создать новый список",
                    callback_data="create_list"
                )
            ],
        ]
    )


def get_lists_keyboard(lists) -> InlineKeyboardMarkup:
    keyboard = []

    for l in lists:
        keyboard.append([
            InlineKeyboardButton(
                text=l.title,
                callback_data=f"list:select:{l.id}"
            )
        ])

    # дополнительные кнопки
    keyboard.append([
        InlineKeyboardButton(
            text="➕ Добавить новый список",
            callback_data="list:create"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            text="🗑  Удалить список",
            callback_data="list:delete"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад в главное меню",
            callback_data="menu:main"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_tasks_keyboard(tasks) -> InlineKeyboardMarkup:
    keyboard = []

    for task in tasks:
        keyboard.append([
            InlineKeyboardButton(
                text=f"✅ {task.value}" if task.completed else f"⬜️ {task.value}",
                callback_data=f"task:select:{task.id}"
            )
        ])

    # дополнительные кнопки
    keyboard.append([
        InlineKeyboardButton(
            text="➕ Добавить новую задачу",
            callback_data="task:create"
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад к спискам",
            callback_data="show_lists"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)