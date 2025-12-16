from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from application.user.create_user import UserService
from presentation.telegram.texts import get_main_menu_text, get_no_lists_text, get_no_tasks_text, get_lists_text, \
    get_tasks_text
from presentation.telegram.keyboards import get_main_menu_keyboard, get_lists_keyboard, get_tasks_keyboard

router = Router()


@router.callback_query(F.data == "menu:main")
async def go_to_main_menu(callback: CallbackQuery):
    """
    Обработчик кнопки 'Назад в главное меню'
    """
    await callback.message.edit_text(
        text=get_main_menu_text(),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

    # Закрываем "часики" на кнопке
    await callback.answer()


@router.callback_query(F.data == "show_lists")
async def show_lists(callback: CallbackQuery, service: UserService):
    """
    Обработчик кнопки 'Посмотреть списки'
    """
    user = service.get_user_by_id(callback.from_user.id)

    if not user.listoftasks:
        # если списков нет, просто отправляем сообщение
        await callback.message.answer(get_no_lists_text())
        await callback.answer()
        return

    text = get_lists_text()
    await callback.message.edit_text(text=text,
                                     parse_mode="Markdown",
                                     reply_markup=get_lists_keyboard(user.listoftasks))

    await callback.answer()  # обязательно закрываем "часики"


@router.callback_query(F.data.startswith("list:select"))
async def show_list(callback: CallbackQuery, service: UserService):
    _, action, list_id = callback.data.split(":")
    list_id = int(list_id)
    listoftask = service.get_list_by_id(callback.from_user.id, list_id)
    tasks = service.get_tasks(callback.from_user.id, list_id)


    if not tasks:
        # если задач нет, просто отправляем сообщение
        await callback.message.answer(get_no_tasks_text())
        await callback.answer()
        return

    text = get_tasks_text(listoftask.title)
    await callback.message.edit_text(text=text,
                                     parse_mode="Markdown",
                                     reply_markup=get_tasks_keyboard(tasks))

    await callback.answer()  # обязательно закрываем "часики"

@router.callback_query(F.data.startswith("list:delete"))
async def delete_list(callback: CallbackQuery, service: UserService):
    user = service.get_user_by_id(callback.from_user.id)