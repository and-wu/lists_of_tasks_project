
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from application.user.create_user import UserService
from presentation.telegram.keyboards.list_keyboards import get_main_menu_keyboard
from presentation.telegram.texts import BotMessages

commands_router = Router()
bot_messages = BotMessages()

# ==============================
#            /start
# ==============================

@commands_router.message(CommandStart())
async def cmd_start(message: Message, service: UserService):
    """Обработчик для команды /start."""
    try:
        service.create_user(user_id=message.from_user.id, name=message.from_user.first_name,
                            username=message.from_user.username)
    except Exception as e:
        print(e)

    text = (
            bot_messages.say_hello(username=message.from_user.first_name)
            + "\n\n"
            + bot_messages.main_menu
    )

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(),
    )
