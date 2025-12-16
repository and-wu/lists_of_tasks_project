from aiogram import Router, F
from aiogram.filters import state
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from application.user.create_user import UserService
from presentation.telegram.states.list_states import ListStates
from presentation.telegram.states.task_states import TaskStates
from presentation.telegram.texts import get_main_menu_text, get_no_lists_text, get_no_tasks_text, get_lists_text, \
    get_tasks_text, get_list_name_prompt, get_list_created_text, get_task_name_prompt, get_task_created_text
from presentation.telegram.keyboards import get_main_menu_keyboard, get_lists_keyboard, get_tasks_keyboard, extra_task_menu


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
    text = get_lists_text() if user.listoftasks else get_no_lists_text()

    await callback.message.edit_text(text=text,
                            parse_mode="Markdown",
                            reply_markup=get_lists_keyboard(user.listoftasks))

    await callback.answer()  # обязательно закрываем "часики"

@router.callback_query(F.data == "create_list")
async def create_list(callback: CallbackQuery, state: FSMContext):

    await state.set_state(ListStates.waiting_for_list_name)  # ставим состояние
    await callback.message.edit_text(get_list_name_prompt())  # просим ввести название
    await callback.answer()  # закрываем "часики"


@router.callback_query(F.data.startswith("list:select"))
async def show_tasks(callback: CallbackQuery, service: UserService):
    _, action, list_id = callback.data.split(":")

    user_id = callback.from_user.id
    list_id = int(list_id)
    task_list = service.get_list_by_id(user_id, list_id)
    tasks = service.get_tasks(user_id, list_id)


    if not tasks:
        # если задач нет, просто отправляем сообщение
        await callback.message.edit_text(text=get_no_tasks_text(task_list.title),
                                         reply_markup=extra_task_menu(list_id=list_id))
        await callback.answer()
        return

    text = get_tasks_text(task_list.title)
    await callback.message.edit_text(text=text,
                                     parse_mode="Markdown",
                                     reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id))

    await callback.answer()  # обязательно закрываем "часики"

@router.callback_query(F.data.startswith("list:delete"))
async def delete_list(callback: CallbackQuery, service: UserService):
    user = service.get_user_by_id(callback.from_user.id)


# -------------------------------
# Message: пользователь вводит название списка
# -------------------------------
@router.message(ListStates.waiting_for_list_name)
async def process_list_name(message: Message, state: FSMContext, service: UserService):
    """
    Обрабатывает текст пользователя, создаёт новый список и сбрасывает состояние.
    """
    list_title = message.text.strip()

    # Добавляем список через сервис
    service.add_list_of_tasks(message.from_user.id, title=list_title)

    user = service.get_user_by_id(message.from_user.id)

    text = get_list_created_text(list_title=list_title) + "\n\n"

    text += get_lists_text() if user.listoftasks else get_no_lists_text()

    await message.answer(text=text,
                            parse_mode="Markdown",
                            reply_markup=get_lists_keyboard(user.listoftasks))

    # Сбрасываем состояние
    await state.clear()

@router.callback_query(F.data.startswith("task:create"))
async def create_task(callback: CallbackQuery, state: FSMContext):
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    # сохраняем id списка в состоянии
    await state.update_data(list_id=list_id)

    # ставим состояние ожидания текста задачи
    await state.set_state(TaskStates.waiting_for_task_text) # ставим состояние

    await callback.message.edit_text(get_task_name_prompt()) # просим ввести текст задачи
    await callback.answer()

@router.message(TaskStates.waiting_for_task_text)
async def process_task_text(message: Message, state: FSMContext, service: UserService):
    task_text = message.text.strip()

    if not task_text:
        await message.answer("Текст задачи не может быть пустым. Попробуйте снова:")
        return

    # достаём сохранённые данные
    data = await state.get_data()
    list_id = data["list_id"]

    # создаём задачу
    task = service.add_task(user_id=message.from_user.id,
                            list_id=list_id,
                            value=task_text
                            )

    text = get_task_created_text(task) + "\n\n"
    text += get_tasks_text(list_title=service.get_list_by_id(user_id=message.from_user.id, list_id=list_id).title)
    tasks = service.get_tasks(message.from_user.id, list_id)

    await message.answer(text=text,
                         parse_mode="Markdown",
                         reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id))    # очищаем состояние
    await state.clear()