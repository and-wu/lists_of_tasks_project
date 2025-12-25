import contextlib
from datetime import time

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from application.scheduler.reminder_scheduler import ReminderScheduler
from application.usecases.lists import AddRemindTimeUseCase, CreateNewListUseCase
from application.user.create_user import UserService
from presentation.telegram.keyboards.cancel_keyboard import get_cancel_keyboard
from presentation.telegram.keyboards.list_keyboards import (
    get_confirm_delete_keyboard,
    get_lists_for_delete_keyboard,
    get_lists_keyboard,
    get_main_menu_keyboard,
    get_yes_no_keyboard,
)
from presentation.telegram.states.list_states import ListStates
from presentation.telegram.texts import ListView

router = Router()

list_view = ListView()


@router.callback_query(F.data == "menu:main")
async def go_to_main_menu(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Назад в главное меню'."""
    await callback.message.edit_text(
        text=list_view.main_menu,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


async def show_lists_view(
    callback: CallbackQuery,
    service: UserService,
    prefix_text: str = "",
) -> None:
    """Отображает список задач пользователя."""
    text = prefix_text if prefix_text else ""
    user = service.get_user_by_id(callback.from_user.id)
    text += list_view.lists_text_header if user.listoftasks else list_view.no_lists

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=get_lists_keyboard(user.listoftasks),
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text=text,
            parse_mode="Markdown",
            reply_markup=get_lists_keyboard(user.listoftasks),
        )


@router.callback_query(F.data == "lists:show")
async def show_lists(callback: CallbackQuery, service: UserService) -> None:
    """Обработчик кнопки 'Посмотреть списки'."""
    await show_lists_view(callback=callback, service=service)
    await callback.answer()


async def remind_show_list(callback: CallbackQuery, service: UserService) -> None:
    """Запускается в нужное время как напоминание."""
    await show_lists_view(callback=callback, service=service)


@router.callback_query(F.data == "list:create")
async def create_list(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик кнопки 'Создать список / Добавить новый список'."""
    await state.set_state(ListStates.waiting_for_list_name)  # ставим состояние
    sent_message = await callback.message.edit_text(
        list_view.list_name_prompt,
        reply_markup=get_cancel_keyboard("list"),
    )

    await state.update_data(prompt_message_id=sent_message.message_id)
    await callback.answer()


@router.message(ListStates.waiting_for_list_name)
async def process_list_name(
    message: Message,
    state: FSMContext,
    service: UserService,
) -> None:
    """Обрабатывает текст пользователя, создаёт новый список и сбрасывает состояние."""
    list_title = message.text.strip()

    if not list_title:
        await message.answer(
            text=list_view.list_name_empty,
            reply_markup=get_cancel_keyboard("list"),
        )
        return

    new_list_tasks = await CreateNewListUseCase(user_service=service).execute(
        user_id=message.from_user.id,
        list_title=list_title,
    )

    await state.update_data(
        list_title=list_title,
        user_message_id=message.message_id,
        new_list_tasks_id=new_list_tasks.id,
    )

    await message.answer(
        text=list_view.wanna_add_remind_for_this_list,
        reply_markup=get_yes_no_keyboard(),
    )

    await state.set_state(ListStates.waiting_for_remind_decision)


@router.callback_query(
    ListStates.waiting_for_remind_decision,
    F.data.in_(["list_remind_yes", "list_remind_no"]),
)
async def process_remind_decision(
    callback: CallbackQuery,
    state: FSMContext,
    service: UserService,
) -> None:
    data = await state.get_data()
    user_message_id = data.get("user_message_id")

    await delete_fsm_prompt_message(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id,
    )

    if user_message_id:
        with contextlib.suppress(TelegramForbiddenError):
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=user_message_id,
            )

    if callback.data == "list_remind_no":
        await show_lists_view(callback=callback, service=service)
        await state.clear()
        return

    edited_message = await callback.message.edit_text(
        text="Введите время напоминания в формате HH:MM (например 09:00)",
    )

    await state.update_data(remind_prompt_message_id=edited_message.message_id)

    await state.set_state(ListStates.waiting_for_remind_time)


@router.message(ListStates.waiting_for_remind_time)
async def process_remind_time(
    message: Message,
    state: FSMContext,
    service: UserService,
    reminder_scheduler: ReminderScheduler,
) -> None:
    try:
        hours, minutes = map(int, message.text.split(":"))
        remind_time = time(hour=hours, minute=minutes)
    except Exception:
        await message.answer("❌ Неверный формат. Введите время как HH:MM")
        return

    use_case = AddRemindTimeUseCase(
        scheduler=reminder_scheduler,
    )

    data = await state.get_data()
    list_title = data["list_title"]
    remind_prompt_message_id = data.get("remind_prompt_message_id")
    new_list_tasks_id = data.get("new_list_tasks_id")

    if remind_prompt_message_id:
        with contextlib.suppress(TelegramForbiddenError):
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=remind_prompt_message_id,
            )

    await use_case.execute(
        user_id=message.from_user.id,
        list_id=new_list_tasks_id,
        remind_time=remind_time,
    )

    with contextlib.suppress(TelegramForbiddenError):
        await message.delete()

    user = service.get_user_by_id(message.from_user.id)
    text = (
        list_view.list_created(list_title=list_title)
        + "\n"
        + f"⏰ Напоминание: {remind_time.strftime('%H:%M')}\n\n"
    )
    text += list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await message.answer(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_lists_keyboard(user.listoftasks),
    )

    await state.clear()


@router.callback_query(F.data == "list:cancel")
async def cancel_action(
    callback: CallbackQuery,
    state: FSMContext,
    service: UserService,
) -> None:
    """Отмена текущего действия (FSM)."""
    await delete_fsm_prompt_message(
        state=state,
        bot=callback.bot,
        chat_id=callback.message.chat.id,
    )

    await state.clear()

    await show_lists_view(callback=callback, service=service)

    await callback.answer(list_view.action_canceled)


@router.callback_query(F.data == "list:delete")
async def delete_list_start(callback: CallbackQuery, service: UserService) -> None:
    user = service.get_user_by_id(callback.from_user.id)
    if not user.listoftasks:
        await callback.message.edit_text(list_view.no_lists)
        await callback.answer()
        return

    await callback.message.edit_text(
        text=list_view.list_delete_choice_prompt,
        reply_markup=get_lists_for_delete_keyboard(user.listoftasks),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("list:confirm_delete:"))
async def confirm_delete(callback: CallbackQuery, service: UserService) -> None:
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    list_to_delete = service.get_list_by_id(callback.from_user.id, list_id)

    if not list_to_delete:
        await callback.answer("Список не найден", show_alert=True)
        return

    await callback.message.edit_text(
        text=list_view.confirm_delete_list(list_to_delete.title),
        reply_markup=get_confirm_delete_keyboard(list_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("list:delete_yes:"))
async def delete_list_confirm(callback: CallbackQuery, service: UserService) -> None:
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    service.delete_list_of_tasks(callback.from_user.id, list_id)

    text = list_view.list_deleted_success

    await show_lists_view(callback=callback, service=service, prefix_text=text)
    await callback.answer(text=list_view.list_deleted_success)


@router.callback_query(F.data.startswith("list:delete_no:"))
async def delete_list_cancel(callback: CallbackQuery, service: UserService) -> None:
    await show_lists_view(callback=callback, service=service)
    await callback.answer(text=list_view.delete_action_canceled)


@router.callback_query(F.data == "list:delete_cancel")
async def cancel_delete_start(callback: CallbackQuery, service: UserService) -> None:
    await show_lists_view(callback=callback, service=service)
    await callback.answer(text=list_view.delete_action_canceled)


async def delete_fsm_prompt_message(state: FSMContext, bot: Bot, chat_id: int) -> None:
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if not prompt_message_id:
        return

    with contextlib.suppress(TelegramForbiddenError):
        await bot.delete_message(
            chat_id=chat_id,
            message_id=prompt_message_id,
        )
