# keyboards.py (или где у вас клавиатуры)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_notification_type_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа уведомлений при создании списка.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⏰ Напоминание",
                callback_data="notification:reminder"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Опрос",
                callback_data="notification:poll"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫 Без уведомлений",
                callback_data="notification:none"
            )
        ],
    ])
    return keyboard


def get_repeat_type_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора периодичности напоминаний.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔂 Ежедневно",
                callback_data="repeat:daily"
            )
        ],
        [
            InlineKeyboardButton(
                text="💼 Будни (Пн-Пт)",
                callback_data="repeat:weekdays"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎉 Выходные (Сб-Вс)",
                callback_data="repeat:weekends"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 Определённые дни недели",
                callback_data="repeat:custom"
            )
        ],
        [
            InlineKeyboardButton(
                text="📌 Определенные даты\n(один или несколько раз)",
                callback_data="repeat:once"
            )
        ]
    ])
    return keyboard

def get_confirm_toggle_notification_keyboard(list_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения смены типа уведомления
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, сменить",
                    callback_data=f"confirm_toggle_notification:{list_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"list:remind_cancel:{list_id}"
                )
            ]
        ]
    )

def get_back_to_notification_type_button() -> InlineKeyboardButton:
    """
    Кнопка возврата к выбору типа уведомления
    """
    return InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back:notification_type"
    )