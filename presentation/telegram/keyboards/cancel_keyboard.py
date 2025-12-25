from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_cancel_keyboard(entity: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"{entity}:cancel",
                ),
            ],
        ],
    )
