from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from application.user.create_user import UserService
from presentation.telegram.keyboards.list_keyboards import get_main_menu_keyboard
from presentation.telegram.states.start_states import StartStates
from presentation.telegram.texts import BotMessages
from presentation.telegram.utils.fsm_cleanup import delete_fsm_prompt_message

commands_router = Router()
bot_messages = BotMessages()

# ==============================
#            /start
# ==============================

@commands_router.message(Command("main_menu"))
async def main_menu(message: Message, state: FSMContext):
    """Обработчик для команды /main menu."""

    chat_id = message.chat.id

    # удаляем сообщение пользователя (/main_menu)
    try:
        await message.delete()
    except Exception:
        pass

    # пытаемся удалить приветственное сообщение (если есть)
    data = await state.get_data()
    greeting_id = data.get("start_message_id")

    if greeting_id:
        try:
            await message.bot.delete_message(chat_id, greeting_id)
        except Exception:
            pass

    # отправляем главное меню
    sent = await message.answer(
        bot_messages.main_menu,
        reply_markup=get_main_menu_keyboard()
    )

    # обновляем ID текущего "главного" сообщения
    await state.update_data(
        greeting_message_id=sent.message_id
    )

@commands_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, service: UserService):
    """Обработчик для команды /start."""

    # удаляем сообщение пользователя (/start)
    try:
        await message.delete()
    except Exception:
        pass


    try:
        service.create_user(user_id=message.from_user.id, name=message.from_user.first_name,
                            username=message.from_user.username)
    except Exception as e:
        print(e)

    user = service.get_or_create_user(
        user_id=message.from_user.id,
        name=message.from_user.first_name,
        username=message.from_user.username
    )

    # ✅ если таблица уже есть — НЕ спрашиваем
    if user.google_sheet_url:
        text = (
                bot_messages.say_hello(username=message.from_user.first_name)
        )

        sent = await message.answer(
            text,
        )

        await state.update_data(start_message_id=sent.message_id)

        return

    text = (
            bot_messages.say_hello(username=message.from_user.first_name)
            + "\n\n"
            + "📊 Пришлите ссылку на Google Таблицу,\n"
              "в которую бот будет сохранять статистику задач."
    )

    sent = await message.answer(
        text,
        reply_markup=None
    )

    # сохраняем prompt
    await state.update_data(prompt_message_id=sent.message_id)
    await state.set_state(StartStates.waiting_for_google_sheet_link)

@commands_router.message(StartStates.waiting_for_google_sheet_link)
async def process_google_sheet_link(message: Message,
                                    state: FSMContext,
                                    service: UserService
                                    ):
    link = message.text.strip()

    # ❌ НЕПРАВИЛЬНАЯ ССЫЛКА

    if not link.startswith("https://docs.google.com/spreadsheets"):
        # удаляем сообщение пользователя
        try:
            await message.delete()
        except Exception:
            pass

        # удаляем прошлый prompt бота
        await delete_fsm_prompt_message(
            state=state,
            bot=message.bot,
            chat_id=message.chat.id
        )

    if not link.startswith("https://docs.google.com/spreadsheets"):
        sent =await message.answer(
            "❌ Это не похоже на ссылку на Google Таблицу.\n"
            "Пришлите корректную ссылку."
        )

        await state.update_data(prompt_message_id=sent.message_id)
        return

    # ✅ ПРАВИЛЬНАЯ ССЫЛКА

    # сохраняем ссылку пользователю
    service.set_google_sheet(
        user_id=message.from_user.id,
        sheet_url=link
    )

    # чистим prompt
    await delete_fsm_prompt_message(
        state=state,
        bot=message.bot,
        chat_id=message.chat.id
    )

    # удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer(
        "✅ Готово! Таблица сохранена.\n\n"
        + bot_messages.main_menu,
        reply_markup=get_main_menu_keyboard()
    )

    await state.clear()
