from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

HIDE_MENU_BUTTON = InlineKeyboardButton(
    text="🙈 Скрыть меню",
    callback_data="menu:hide"
)

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Посмотреть списки",
                    callback_data="lists:show"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Создать новый список",
                    callback_data="list:create"
                )
            ],
            [
                HIDE_MENU_BUTTON
             ]
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
    keyboard.append([HIDE_MENU_BUTTON
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_lists_for_delete_keyboard(lists):
    """
    Список списков для выбора, какой удалять
    """
    keyboard = []
    for lst in lists:
        keyboard.append([
            InlineKeyboardButton(
                text=lst.title,
                callback_data=f"list:confirm_delete:{lst.id}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="list:delete_cancel"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_delete_keyboard(list_id):
    """
    Подтверждение удаления конкретного списка
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"list:delete_yes:{list_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data=f"list:delete_no:{list_id}")
            ]
        ]
    )


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data="list_remind_yes"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="list_remind_no"
                )
            ]
        ]
    )
