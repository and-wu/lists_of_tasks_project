from aiogram.types import Message
from domain.users import User
from presentation.telegram.keyboards import get_lists_keyboard
from presentation.telegram.texts import get_lists_text, get_no_lists_text


async def show_lists_menu(message: Message, user: User):
    text = get_lists_text() if user.listoftasks else get_no_lists_text()

    await message.edit_text(text=text,
                                     parse_mode="Markdown",
                                     reply_markup=get_lists_keyboard(user.listoftasks))