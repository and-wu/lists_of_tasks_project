import builtins
import contextlib
from datetime import time

from aiogram import Router, F
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from application.scheduler.reminder_scheduler import ReminderScheduler
from application.user.create_user import UserService
from presentation.telegram.keyboards.extra_keyboard import get_cancel_keyboard
from presentation.telegram.states.list_states import ListStates
from presentation.telegram.states.task_states import TaskStates
from presentation.telegram.texts import TaskView
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard, extra_task_menu, \
    get_task_detail_keyboard, get_confirm_delete_task_keyboard, remind_manage_keyboard_with_time, \
    remind_manage_keyboard_without_time
from presentation.telegram.utils.fsm_cleanup import delete_fsm_prompt_message

router = Router()

task_view = TaskView()

@router.callback_query(F.data.startswith("list:select"))
async def show_tasks(callback: CallbackQuery, service: UserService):
    """Обработчик для отображения задач."""
    _, action, list_id = callback.data.split(":")

    user_id = callback.from_user.id
    list_id = int(list_id)
    task_list = service.get_list_by_id(user_id, list_id)
    tasks = service.get_tasks(user_id=user_id, list_of_tasks_id=list_id)


    if not tasks:
        # если задач нет, просто отправляем сообщение
        await callback.message.edit_text(text=task_view.no_tasks_in_list(task_list.title),
                                         reply_markup=extra_task_menu(list_id=list_id))
        await callback.answer()
        return

    text = task_view.get_list_title(task_list.title)
    await callback.message.edit_text(text=text,
                                     reply_markup=get_tasks_keyboard(tasks=tasks,
                                                                     list_id=list_id,
                                                                     tasks_list=task_list)
                                     )

    await callback.answer()  # обязательно закрываем "часики"



@router.callback_query(F.data.startswith("task:create"))
async def create_task(callback: CallbackQuery, state: FSMContext):
    """Обработчик для старта создания новой задачи."""
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)
    sent_message = await callback.message.edit_text(task_view.task_name_prompt,
                                                    reply_markup=get_cancel_keyboard("task"))  # просим ввести текст задачи


    # ставим состояние ожидания текста задачи
    await state.set_state(TaskStates.waiting_for_task_text) # ставим состояние

    # сохраняем id списка в состоянии и ID сообщения бота
    await state.update_data(list_id=list_id, prompt_message_id=sent_message.message_id)

    await callback.answer()

@router.message(TaskStates.waiting_for_task_text)
async def process_task_text(message: Message, state: FSMContext, service: UserService):
    """Обработчик для заголовка новой задачи."""
    task_text = message.text.strip()

    if not task_text:
        await message.answer(task_view.task_name_empty,
                             reply_markup=get_cancel_keyboard("task"))
        return

    # достаём сохранённые данные
    data = await state.get_data()
    list_id = data["list_id"]

    # 3 Вынести в UseCase.
    # создаём задачу
    task = service.add_task(user_id=message.from_user.id,
                            list_id=list_id,
                            value=task_text
                            )

    await delete_fsm_prompt_message(state=state, bot=message.bot, chat_id=message.chat.id)

    # удаляем сообщение пользователя
    try:
        await message.delete()
    except TelegramForbiddenError:
        pass

    await state.clear()  # очищаем состояние

    task_list = service.get_list_by_id(user_id=message.from_user.id, list_id=list_id)
    tasks = service.get_tasks(user_id=message.from_user.id, list_of_tasks_id=list_id)

    text = task_view.task_created(task) + "\n\n"
    text += task_view.get_list_title(task_list.title)

    await message.answer(text=text,
                         reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id))



@router.callback_query(F.data == "task:cancel")
async def cancel_action_create(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Отмена текущего действия (FSM)
    """
    # достаём сохранённые данные
    data = await state.get_data()
    list_id = data.get("list_id")

    # очищаем состояние
    await state.clear()

    user_id = callback.from_user.id

    task_list = service.get_list_by_id(user_id=user_id, list_id=list_id)
    tasks = service.get_tasks(user_id=user_id, list_of_tasks_id=list_id)

    text = task_view.get_list_title(task_list.title)

    await callback.message.edit_text(text=text,
                         reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id))

    await callback.answer()


@router.callback_query(F.data.startswith("task:select"))
async def select_task(callback: CallbackQuery, service: UserService):
    """Обработчик выбора задачи."""
    _, _, task_id = callback.data.split(":")
    task_id = int(task_id)

    task, list_id = service.get_task_with_list(callback.from_user.id, task_id)

    text = task_view.task_text(task)

    await callback.message.edit_text(
        text=text,
        reply_markup=get_task_detail_keyboard(task, list_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task:edit:"))
async def edit_task(callback: CallbackQuery, state: FSMContext, service: UserService):
    """Обработчик редактирования задачи."""
    _, _, task_id = callback.data.split(":")
    task_id = int(task_id)

    task, list_id = service.get_task_with_list(callback.from_user.id, task_id)

    await state.update_data(task_id=task_id, list_id=list_id)
    await state.set_state(TaskStates.waiting_for_new_task_text)

    text = task_view.task_new_text_prompt(task)

    sent_message = await callback.message.edit_text(text=text,
                                     parse_mode="HTML",
                                     reply_markup=get_cancel_keyboard("task_text")
                                     )
    # сохраняем ID сообщения в FSM, чтобы потом удалить
    await state.update_data(prompt_message_id=sent_message.message_id)

    await callback.answer()

@router.message(TaskStates.waiting_for_new_task_text)
async def process_new_task_text(message: Message,state: FSMContext,service: UserService):
    """Обработчик создания нового текста задачи."""
    new_text = message.text.strip()

    if not new_text:
        await message.answer(
            text=task_view.task_name_empty,
            reply_markup=get_cancel_keyboard("task_text")
        )
        return

    data = await state.get_data()
    task_id = data["task_id"]
    list_id = data["list_id"]

    # удаляем сообщение с приглашением к вводу
    prompt_message_id = data.get("prompt_message_id")
    if prompt_message_id:
        with contextlib.suppress(builtins.BaseException):
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)

    # удаляем сообщение пользователя
    try:
        await message.delete()
    except:
        pass

    # обновляем задачу
    task = service.update_task_text(
        user_id=message.from_user.id,
        task_id=task_id,
        new_value=new_text
    )

    await state.clear()

    text = task_view.task_updated_success(task=task)

    await message.answer(
        text=text,
        reply_markup=get_task_detail_keyboard(task, list_id)
    )


@router.callback_query(F.data.startswith("tasks:back:"))
async def back_to_tasks(callback: CallbackQuery, service: UserService):
    """Обработчик перехода назад к списку списков задач."""
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    user_id = callback.from_user.id

    task_list = service.get_list_by_id(user_id=user_id, list_id=list_id)
    if not task_list:
        await callback.message.edit_text(text=task_view.list_not_found_error)
        await callback.answer()
        return

    tasks = service.get_tasks(user_id=user_id, list_of_tasks_id=list_id)

    await callback.message.edit_text(
        text=task_view.get_list_title(task_list.title),
        reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id)
    )

    await callback.answer()


@router.callback_query(F.data == "task_text:cancel")
async def cancel_action_edit_task(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Отмена текущего действия (FSM)
    """
    # достаём сохранённые данные
    data = await state.get_data()
    task_id = data["task_id"]

    # очищаем состояние
    await state.clear()


    task, list_id = service.get_task_with_list(callback.from_user.id, task_id)

    text = task_view.task_text(task)

    await callback.message.edit_text(
        text=text,
        reply_markup=get_task_detail_keyboard(task, list_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("task:toggle:"))
async def toggle_task_completed(callback: CallbackQuery, service: UserService):
    """Обработчик переключению статуса задачи."""
    _, _, task_id = callback.data.split(":")
    task_id = int(task_id)

    user_id = callback.from_user.id

    # получаем задачу и список, в котором она лежит
    task, list_id = service.get_task_with_list(user_id, task_id)

    # переключаем статус
    task = service.toggle_task_completed(user_id, task_id)

    text = task_view.task_text(task)

    await callback.message.edit_text(
        text=text,
        reply_markup=get_task_detail_keyboard(task, list_id)
    )

    await callback.answer(text=task_view.status_updated_success)

@router.callback_query(F.data.startswith("task:delete:"))
async def delete_task(callback: CallbackQuery, service: UserService):
    """
    Обработчик удаления задачи.

    Вызывает контекстное окно "Да/Нет".
    """
    _, _, task_id = callback.data.split(":")
    task_id = int(task_id)

    task, list_id = service.get_task_with_list(
        callback.from_user.id,
        task_id
    )

    await callback.message.edit_text(
        text=task_view.confirm_delete_task(task.value),
        reply_markup=get_confirm_delete_task_keyboard(task_id, list_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("tasks:delete:yes:"))
async def delete_task_yes(callback: CallbackQuery, service: UserService):
    """Обработчик подтверждения удаления задачи."""
    parts = callback.data.split(":")
    task_id = int(parts[-2])
    list_id = int(parts[-1])

    service.delete_task(user_id=callback.from_user.id,task_id=task_id)

    task_list = service.get_list_by_id(callback.from_user.id,list_id)
    tasks = service.get_tasks(callback.from_user.id, list_id)

    text = task_view.task_delete_success
    text += (task_view.get_list_title(task_list.title) if tasks else task_view.no_tasks_in_list(task_list.title))

    await callback.message.edit_text(text=text,
                                     reply_markup=get_tasks_keyboard(tasks, list_id)
                                     )

    await callback.answer(text=task_view.task_delete_success)

@router.callback_query(F.data.startswith("tasks:delete:no:"))
async def delete_task_no(callback: CallbackQuery, service: UserService):
    """Обработчик отмены удаления задачи."""
    parts = callback.data.split(":")
    task_id = int(parts[-2])
    list_id = int(parts[-1])

    task, _ = service.get_task_with_list(user_id=callback.from_user.id,
                                         task_id=task_id
                                         )

    await callback.message.edit_text(text=task_view.task_text(task),
                                     reply_markup=get_task_detail_keyboard(task, list_id)
                                     )

    await callback.answer(text=task_view.delete_action_canceled)


@router.callback_query(lambda c: c.data.startswith("list:remind_menu:"))
async def open_remind_menu(
    callback: CallbackQuery,
    service: UserService
):
    list_id = int(callback.data.split(":")[-1])
    task_list = service.get_list_by_id(callback.from_user.id, list_id)

    if task_list is None:
        await callback.answer("❌ Список не найден")
        return

    # выбираем нужную клавиатуру
    if task_list.remind_time:
        keyboard = remind_manage_keyboard_with_time(list_id, remind_time=task_list.remind_time)
    else:
        keyboard = remind_manage_keyboard_without_time(list_id)

    # 🔁 заменяем клавиатуру у текущего сообщения
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith(("list:remind_add:", "list:remind_edit:")))
async def remind_time_callback(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Колбек для кнопок добавления/изменения времени
    Пользователь нажал 'Добавить время' или 'Изменить время'.
    """
    list_id = int(callback.data.split(":")[-1])
    task_list = service.get_list_by_id(callback.from_user.id, list_id)

    if not task_list:
        await callback.answer("❌ Список не найден")
        return

    try:
        await callback.message.delete()
    except Exception:
        pass

    # Сохраняем ID списка в FSM, чтобы хэндлер ввода времени знал, для какого списка ввод
    await state.update_data(edit_list_id=list_id)

    # Переводим пользователя в состояние ожидания времени
    await state.set_state(ListStates.waiting_for_edit_remind_time)

    # отправляем сообщение с инструкцией и сохраняем её message_id
    if task_list.remind_time:
        msg = await callback.message.answer(
            f"Текущее время напоминания: {task_list.remind_time.strftime('%H:%M')}\n"
            "Введите новое время в формате HH:MM"
        )
    else:
        msg = await callback.message.answer(
            "Введите время напоминания для этого списка в формате HH:MM",
        )

    await state.update_data(remind_prompt_message_id=msg.message_id)

    # Закрываем всплывающее уведомление колбека
    await callback.answer()

@router.message(ListStates.waiting_for_edit_remind_time)
async def edit_remind_time(message: Message, state: FSMContext,
                           service: UserService, reminder_scheduler: ReminderScheduler):
    """
    Хэндлер для изменения времени напоминания существующего списка.
    Ожидает ввод времени в формате HH:MM.
    """

    # 0️⃣ Удаляем старое сообщение ошибки (если есть)
    data = await state.get_data()
    remind_error_message_id = data.get("remind_error_message_id")
    if remind_error_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=remind_error_message_id
            )
        except TelegramForbiddenError:
            pass

    # 1️⃣ Парсим введённое время
    try:
        hours, minutes = map(int, message.text.split(":"))
        new_time = time(hour=hours, minute=minutes)
    except Exception:
        # удаляем сообщение пользователя
        try:
            await message.delete()
        except TelegramForbiddenError:
            pass

        # отправляем сообщение об ошибке и сохраняем его ID
        error_msg = await message.answer("❌ Неверный формат времени. Введите как HH:MM")
        await state.update_data(remind_error_message_id=error_msg.message_id)
        return

    # 2️⃣ Берём из state id списка, который редактируем
    list_id = data.get("edit_list_id")
    prompt_message_id = data.get("remind_prompt_message_id")

    if list_id is None:
        await message.answer("❌ Ошибка: список не найден.")
        await state.clear()
        return

    task_list = service.get_list_by_id(message.from_user.id, list_id)
    if task_list is None:
        await message.answer("❌ Ошибка: не найден список.")
        await state.clear()
        return

    # 3️⃣ Обновляем время через ReminderScheduler
    reminder_scheduler.update_list_remind_time(
        user_id=message.from_user.id,
        list_id=list_id,
        new_time=new_time
    )

    # 4️⃣ Сохраняем новое время в объекте списка
    task_list.remind_time = new_time
    service.save_user(message.from_user.id)

    # 5️⃣ Удаляем сообщение-инструкцию
    if prompt_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=prompt_message_id
            )
        except TelegramForbiddenError:
            pass

    # 6️⃣ Удаляем сообщение пользователя с временем (если есть права)
    try:
        await message.delete()
    except TelegramForbiddenError:
        pass

    # 7️⃣ Отправляем подтверждение
    await message.answer(
        f"⏰ Время напоминания для списка *{task_list.title}* изменено на {new_time.strftime('%H:%M')}",
        reply_markup=get_tasks_keyboard(task_list.tasks, list_id, tasks_list=task_list)
    )

    # 8️⃣ Чистим state
    await state.clear()

@router.callback_query(lambda c: c.data and c.data.startswith("list:remind_remove:"))
async def remove_remind_time(
    callback: CallbackQuery,
    service: UserService,
    reminder_scheduler: ReminderScheduler
):
    """
    удаляет время напоминания
    """
    # 1️⃣ Достаём list_id
    list_id = int(callback.data.split(":")[-1])

    # 2️⃣ Находим список (ВАЖНО: list_id может быть 0)
    task_list = service.get_list_by_id(callback.from_user.id, list_id)

    if task_list is None:
        await callback.answer("❌ Список не найден")
        return

    # 3️⃣ Если времени и так нет
    if not task_list.remind_time:
        await callback.answer("⏰ У этого списка нет напоминания")
        return

    # 4️⃣ Удаляем напоминание из планировщика
    reminder_scheduler.remove_list_reminder(
        user_id=callback.from_user.id,
        list_id=list_id
    )

    # 5️⃣ Чистим время в объекте списка
    task_list.remind_time = None
    service.save_user(callback.from_user.id)

    # 6️⃣ Обновляем клавиатуру списка задач
    await callback.message.edit_reply_markup(
        reply_markup=get_tasks_keyboard(
            tasks=task_list.tasks,
            list_id=list_id,
            tasks_list=task_list
        )
    )

    # 7️⃣ Всплывающее подтверждение
    await callback.answer("🗑 Время напоминания удалено")

@router.callback_query(lambda c: c.data.startswith("list:remind_cancel:"))
async def cancel_remind_edit(
    callback: CallbackQuery,
    service: UserService
):
    list_id = int(callback.data.split(":")[-1])
    task_list = service.get_list_by_id(callback.from_user.id, list_id)

    if task_list is None:
        await callback.answer("❌ Список не найден")
        return

    await callback.message.edit_reply_markup(
        reply_markup=get_tasks_keyboard(
            tasks=task_list.tasks,
            list_id=list_id,
            tasks_list=task_list
        )
    )
    await callback.answer("↩️ Отменено")

