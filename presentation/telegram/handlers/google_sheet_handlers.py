from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from application.user.create_user import UserService
from presentation.telegram.keyboards.cancel_keyboard import get_cancel_keyboard
from presentation.telegram.keyboards.list_keyboards import get_main_menu_keyboard
from presentation.telegram.states.sheet_states import SheetStates
from presentation.telegram.texts import TaskView, BotMessages
from presentation.telegram.utils.fsm_cleanup import delete_fsm_prompt_message

bot_messages = BotMessages()


router = Router()

task_view = TaskView()

@router.callback_query(lambda c: c.data == "google_sheet:add")
async def add_or_replace_google_sheet_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    """
    Привязка или замена Google-таблицы.
    Если таблица уже была — она будет перезаписана.
    """

    # удаляем сообщение с меню
    try:
        await callback.message.delete()
    except Exception:
        pass

    sent = await callback.message.answer(
        "📊 Пришлите ссылку на Google Таблицу.\n"
              "в которую бот будет сохранять статистику задач.\n\n"
              "Если таблица уже была привязана — она будет заменена.",
        reply_markup=get_cancel_keyboard('google_sheet')
    )

    # сохраняем prompt
    await state.update_data(prompt_message_id=sent.message_id)

    # переводим в тот же FSM, что и при /start
    await state.set_state(SheetStates.waiting_for_google_sheet_link)

    await callback.answer()

@router.message(SheetStates.waiting_for_google_sheet_link)
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

@router.callback_query(F.data == "google_sheet:cancel")
async def cancel_google_sheet_action(callback: CallbackQuery,state: FSMContext):
    """
    Отмена привязки / замены Google-таблицы
    """

    # удаляем prompt-сообщение FSM (если было)
    await delete_fsm_prompt_message(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id
    )

    # чистим состояние
    await state.clear()

    # возвращаем главное меню
    await callback.message.answer(
        bot_messages.main_menu,
        reply_markup=get_main_menu_keyboard()
    )

    # закрываем callback
    await callback.answer("Действие отменено")