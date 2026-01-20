
from aiogram import Router
from aiogram.filters import CommandStart
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

@commands_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, service: UserService):
    """Обработчик для команды /start."""
    try:
        service.create_user(user_id=message.from_user.id, name=message.from_user.first_name,
                            username=message.from_user.username)
    except Exception as e:
        print(e)

    # text = (
    #         bot_messages.say_hello(username=message.from_user.first_name)
    #         + "\n\n"
    #         + bot_messages.main_menu
    # )
    #
    # await message.answer(
    #     text,
    #     reply_markup=get_main_menu_keyboard(),
    # )

    user = service.get_or_create_user(
        user_id=message.from_user.id,
        name=message.from_user.first_name,
        username=message.from_user.username
    )

    # ✅ если таблица уже есть — НЕ спрашиваем
    if user.google_sheet_url:
        text = (
                bot_messages.say_hello(username=message.from_user.first_name)
                + "\n\n"
                + bot_messages.main_menu
        )

        await message.answer(
            text,
            reply_markup=get_main_menu_keyboard()
        )
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
