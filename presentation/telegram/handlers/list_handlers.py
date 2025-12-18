from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from application.user.create_user import UserService
from presentation.telegram.keyboards.cancel_keyboard import get_cancel_keyboard
from presentation.telegram.states.list_states import ListStates
from presentation.telegram.texts import ListView
from presentation.telegram.keyboards.list_keyboards import get_main_menu_keyboard, get_lists_keyboard, \
    get_lists_for_delete_keyboard, get_confirm_delete_keyboard

router = Router()

list_view = ListView()

@router.callback_query(F.data == "menu:main")
async def go_to_main_menu(callback: CallbackQuery):
    """
    Обработчик кнопки 'Назад в главное меню'
    """
    await callback.message.edit_text(
        text=list_view.main_menu,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

    # Закрываем "часики" на кнопке
    await callback.answer()


@router.callback_query(F.data == "lists:show")
async def show_lists(callback: CallbackQuery, service: UserService):
    """
    Обработчик кнопки 'Посмотреть списки'
    """
    user = service.get_user_by_id(callback.from_user.id)
    text = list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await callback.message.edit_text(text=text,
                                     parse_mode="Markdown",
                                     reply_markup=get_lists_keyboard(user.listoftasks))

    await callback.answer()  # обязательно закрываем "часики"


@router.callback_query(F.data == "list:create")
async def create_list(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Создать список / Добавить новый список'
    """

    await state.set_state(ListStates.waiting_for_list_name)  # ставим состояние
    await callback.message.edit_text(list_view.list_name_prompt,
                                     reply_markup=get_cancel_keyboard("list"))  # просим ввести название
    await callback.answer()  # закрываем "часики"


# -------------------------------
# Message: пользователь вводит название списка
# -------------------------------
@router.message(ListStates.waiting_for_list_name)
async def process_list_name(message: Message, state: FSMContext, service: UserService):
    """
    Обрабатывает текст пользователя, создаёт новый список и сбрасывает состояние.
    """
    list_title = message.text.strip()

    if not list_title:
        await message.answer(text=list_view.list_name_empty,
                             reply_markup=get_cancel_keyboard('list')
                             )
        return

    # Добавляем список через сервис
    service.add_list_of_tasks(message.from_user.id, title=list_title)

    user = service.get_user_by_id(message.from_user.id)

    text = list_view.list_created(list_title=list_title) + "\n\n"

    text += list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await message.answer(text=text,
                         parse_mode="Markdown",
                         reply_markup=get_lists_keyboard(user.listoftasks))

    # Сбрасываем состояние
    await state.clear()


@router.callback_query(F.data == "list:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Отмена текущего действия (FSM)
    """
    await state.clear()

    user = service.get_user_by_id(callback.from_user.id)
    text = list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_lists_keyboard(user.listoftasks)
    )

    await callback.answer(list_view.action_canceled)


@router.callback_query(F.data == "list:delete")
async def delete_list_start(callback: CallbackQuery, service: UserService):
    user = service.get_user_by_id(callback.from_user.id)
    if not user.listoftasks:
        await callback.message.edit_text("Списков нет")
        await callback.answer()
        return

    await callback.message.edit_text(
        "Выберите список для удаления:",
        reply_markup=get_lists_for_delete_keyboard(user.listoftasks)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("list:confirm_delete:"))
async def confirm_delete(callback: CallbackQuery, service: UserService):
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    list_to_delete = service.get_list_by_id(callback.from_user.id, list_id)

    await callback.message.edit_text(
        f"Точно удалить список '{list_to_delete.title}'?",
        reply_markup=get_confirm_delete_keyboard(list_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("list:delete_yes:"))
async def delete_list_confirm(callback: CallbackQuery, service: UserService):
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    service.delete_list_of_tasks(callback.from_user.id, list_id)

    user = service.get_user_by_id(callback.from_user.id)
    text = "Список удалён ✅\n\n"
    text += list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_lists_keyboard(user.listoftasks)
    )
    await callback.answer("Список удалён")


@router.callback_query(F.data.startswith("list:delete_no:"))
async def delete_list_cancel(callback: CallbackQuery, service: UserService):
    user = service.get_user_by_id(callback.from_user.id)
    text = list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_lists_keyboard(user.listoftasks)
    )
    await callback.answer("Удаление отменено")


@router.callback_query(F.data == "list:delete_cancel")
async def cancel_delete_start(callback: CallbackQuery, service: UserService):
    user = service.get_user_by_id(callback.from_user.id)
    text = list_view.lists_text_header if user.listoftasks else list_view.no_lists

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_lists_keyboard(user.listoftasks)
    )
    await callback.answer("Отмена")
