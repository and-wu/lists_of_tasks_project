from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_cancel_keyboard(entity: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"{entity}:cancel"
                )
            ]
        ]
    )
