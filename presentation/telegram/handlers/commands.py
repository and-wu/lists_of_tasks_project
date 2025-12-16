
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from application.user.create_user import UserService
from presentation.telegram.keyboards import get_main_menu_keyboard
from presentation.telegram.texts import get_main_menu_text, say_hello

commands_router = Router()


# ==============================
#            /start
# ==============================

@commands_router.message(CommandStart())
async def cmd_start(message: Message, service: UserService):
    try:
        service.create_user(user_id=message.from_user.id, name=message.from_user.first_name,
                            username=message.from_user.username)
    except Exception as e:
        print(e)

    text = (
            say_hello(username=message.from_user.first_name)
            + "\n\n"
            + get_main_menu_text()
    )

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
