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
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="back:notification_type"
            )
        ]
    ])
    return keyboard