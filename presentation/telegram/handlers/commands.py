import contextlib

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from application.user.create_user import UserService
from presentation.telegram.keyboards.list_keyboards import get_main_menu_keyboard
from presentation.telegram.texts import BotMessages

commands_router = Router()
bot_messages = BotMessages()


@commands_router.message(CommandStart())
async def cmd_start(message: Message, service: UserService) -> None:
    """Обработчик для команды /start."""
    with contextlib.suppress(Exception):
        service.create_user(
            user_id=message.from_user.id,
            name=message.from_user.first_name,
            username=message.from_user.username,
        )

    text = (
        bot_messages.say_hello(username=message.from_user.first_name)
        + "\n\n"
        + bot_messages.main_menu
    )

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(),
    )
