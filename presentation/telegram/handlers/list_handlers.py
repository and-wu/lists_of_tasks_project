from datetime import time, datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from application.usecases.lists import CreateNewListUseCase
from application.usecases.update_list_reminder_settings import UpdateListReminderSettingsUseCase
from application.user.create_user import UserService
from domain.enums.notification_type import NotificationType
from domain.enums.repeat_type import RepeatType
from domain.errors import ListAlreadyExistsError
from presentation.telegram.keyboards.calendar_keyboard import get_calendar_keyboard
from presentation.telegram.keyboards.extra_keyboard import get_cancel_keyboard
from presentation.telegram.keyboards.notification_repeat_keyboard import get_notification_type_keyboard, \
    get_repeat_type_keyboard, get_back_to_notification_type_button
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard
from presentation.telegram.keyboards.weekdays_keyboard import get_weekdays_keyboard
from presentation.telegram.states.list_states import ListStates
from presentation.telegram.texts import ListView
from presentation.telegram.keyboards.list_keyboards import (
    get_main_menu_keyboard,
    get_lists_keyboard,
    get_lists_for_delete_keyboard,
    get_confirm_delete_keyboard)
from presentation.telegram.utils.fsm_cleanup import delete_fsm_prompt_message

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
    )

    # Закрываем "часики" на кнопке
    await callback.answer()

async def show_lists_view(callback: CallbackQuery, service: UserService, prefix_text: str = ""):
    """Отображает список задач пользователя"""

    text = prefix_text if prefix_text else ""
    user = service.get_user_by_id(callback.from_user.id)
    text += list_view.lists_text_header if user.listoftasks else list_view.no_lists

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=get_lists_keyboard(user.listoftasks)
        )
    except TelegramBadRequest:
        # сообщение удалено — отправляем новое
        await callback.message.answer(
            text=text,
            reply_markup=get_lists_keyboard(user.listoftasks)
        )

@router.callback_query(F.data == "lists:show")
async def show_lists(callback: CallbackQuery, service: UserService):
    """
    Обработчик кнопки 'Посмотреть списки'
    """
    await show_lists_view(callback=callback, service=service)

    await callback.answer()  # обязательно закрываем "часики"

async def remind_show_list(callback: CallbackQuery, service: UserService):
    """
    Запускается в нужное время как напоминание
    """
    await show_lists_view(callback=callback, service=service)


@router.callback_query(F.data == "list:create")
async def create_list(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Создать список / Добавить новый список'
    """

    await state.set_state(ListStates.waiting_for_list_name)  # ставим состояние
    sent_message = await callback.message.edit_text(list_view.list_name_prompt,
                                     reply_markup=get_cancel_keyboard("list"))  # просим ввести название

    # сохраняем ID сообщения бота
    await state.update_data(prompt_message_id=sent_message.message_id)

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

    # Получаем данные FSM
    data = await state.get_data()

    # Удаляем старое сообщение об ошибке (если было)
    error_message_id = data.get("error_message_id")
    if error_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=error_message_id
            )
        except TelegramBadRequest:
            pass

        # очищаем id
        await state.update_data(error_message_id=None)

    use_case = CreateNewListUseCase(user_service=service)

    try:
        new_list_tasks = await use_case.execute(
            user_id=message.from_user.id,
            list_title=list_title,
        )
    except ListAlreadyExistsError:
        # 🧹 удаляем сообщение пользователя с дублирующим названием
        try:
            await message.delete()
        except TelegramBadRequest:
            pass

        error_message = await message.answer(
            text="❌ Список с таким названием уже существует.\n"
                 "Введите другое название:",
            reply_markup=get_cancel_keyboard('list')
        )

        # сохраняем id сообщения об ошибке
        await state.update_data(error_message_id=error_message.message_id)
        return

    data = await state.get_data()

    # 🧹 удаляем сообщение бота "Введите название списка"
    prompt_message_id = data.get("prompt_message_id")
    if prompt_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=prompt_message_id
            )
        except TelegramBadRequest:
            pass

    # 🧹 удаляем сообщение пользователя с названием списка
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    # ✅ сохраняем ВСЁ нужное в FSM
    await state.update_data(
        list_title=list_title,
        list_id=new_list_tasks.id,
        user_message_id=message.message_id
    )

    # 🆕 Предлагаем выбрать тип уведомлений
    await message.answer(
        text=f"✅ Список *{list_title}* создан!\n\n"
             "Выберите тип уведомлений:",
        reply_markup=get_notification_type_keyboard(),
        parse_mode="Markdown"
    )

    await state.set_state(ListStates.waiting_for_notification_type)


# 🆕 Обработчик выбора типа уведомлений
@router.callback_query(
    ListStates.waiting_for_notification_type,
    F.data.startswith("notification:")
)
async def process_notification_type(callback: CallbackQuery, service: UserService, state: FSMContext):
    """
    Обрабатывает выбор типа уведомлений.
    """
    raw_notification_type = callback.data.split(":")[1]

    data = await state.get_data()
    list_title = data.get("list_title", "")
    user = service.get_user_by_id(callback.from_user.id)

    if raw_notification_type == "none":
        # Без уведомлений - завершаем создание списка
        await callback.message.edit_text(
            f"✅ Список *{list_title}* создан без уведомлений!",
            parse_mode="Markdown",
            reply_markup=get_lists_keyboard(user.listoftasks)
        )
        await state.clear()
        await callback.answer()
        return

    ## 🔥 ВАЖНО: конвертируем строку в enum
    try:
        notification_type = NotificationType(raw_notification_type)
    except ValueError:
        await callback.answer("❌ Неизвестный тип уведомлений", show_alert=True)
        return

    # ✅ В FSM теперь хранится enum, а не строка
    await state.update_data(notification_type=notification_type)

    # Переходим к выбору периодичности
    if notification_type == NotificationType.REMINDER:
        text = "⏰ Выберите периодичность напоминаний:"
    else:  # poll
        text = "📊 Выберите периодичность опросов:"

    builder = InlineKeyboardBuilder()

    # добавляем кнопки периодичности
    for row in get_repeat_type_keyboard().inline_keyboard:
        builder.row(*row)

    # добавляем кнопку отмены
    builder.row(get_back_to_notification_type_button())

    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )

    await state.set_state(ListStates.waiting_for_repeat_type)
    await callback.answer()


# 🆕 Обработчик выбора периодичности
@router.callback_query(
    ListStates.waiting_for_repeat_type,
    F.data.startswith("repeat:")
)
async def process_repeat_type(callback: CallbackQuery, state: FSMContext, service: UserService,
    update_reminder_uc: UpdateListReminderSettingsUseCase,):
    """
    Обрабатывает выбор периодичности уведомлений.
    """
    repeat_type_str = callback.data.split(":")[1]

    # Конвертируем в enum
    repeat_type = RepeatType(repeat_type_str)

    # Сохраняем в state
    await state.update_data(repeat_type=repeat_type)

    data = await state.get_data()
    list_id = data.get("list_id")
    user_id = callback.from_user.id

    task_list = service.get_list_by_id(user_id, list_id)

    # 🔥 Если пользователь выбрал "Один или несколько раз" — показываем календарь
    if repeat_type == RepeatType.ONCE:
        now = datetime.now()
        # Сбрасываем выбранные даты и сохраняем текущий месяц/год
        await state.update_data(selected_dates=[], calendar_year=now.year, calendar_month=now.month)

        await callback.message.edit_text(
            "🗓 Выберите дату/даты для напоминания:",
            reply_markup=get_calendar_keyboard(now.year, now.month, [])
        )

        await state.set_state(ListStates.waiting_for_custom_dates)
        await callback.answer()
        return

    # 🔥 ЕСЛИ CUSTOM — показываем выбор дней
    if repeat_type == RepeatType.CUSTOM:
        await state.update_data(selected_days=[])

        await callback.message.edit_text(
            "🗓 Выберите дни недели:",
            reply_markup=get_weekdays_keyboard([])
        )

        await callback.answer()
        return

    # ---- Остальная логика для всех остальных типов ----

    # Если время уже есть — НЕ спрашиваем заново
    if task_list.remind_time is not None:
        # просто обновляем настройки
        await update_reminder_uc.execute(
            user_id=user_id,
            list_id=list_id,
            remind_time=task_list.remind_time,
            repeat_type=repeat_type,
            run_dates=task_list.run_dates,
            notification_type=task_list.notification_type,
            week_days=task_list.week_days,
        )


        await callback.message.edit_text(
            text=f"✅ Периодичность успешно обновлена на {repeat_type}!",
            reply_markup=get_tasks_keyboard(tasks=task_list.tasks,
                                            list_id=list_id,
                                            tasks_list=task_list),
            parse_mode="Markdown"
        )

        await state.clear()
        await callback.answer()
        return

    # Если времени нет - просим ввести время
    notification_type = data.get("notification_type")

    if notification_type == NotificationType.REMINDER:
        text = "⏰ Введите время напоминания в формате HH:MM\nНапример: 09:00"
    else:  # poll
        text = "📊 Введите время отправки опроса в формате HH:MM\nНапример: 20:00"

    sent_message = await callback.message.edit_text(
        text=text,
        reply_markup=get_cancel_keyboard("list")
    )

    # Сохраняем ID сообщения для последующего удаления
    await state.update_data(time_prompt_message_id=sent_message.message_id)

    await state.set_state(ListStates.waiting_for_remind_time)
    await callback.answer()


# 🆕 Кнопка "Назад" к выбору типа уведомлений
@router.callback_query(
    ListStates.waiting_for_repeat_type,
    F.data == "back:notification_type"
)
async def back_to_notification_type(callback: CallbackQuery, state: FSMContext):
    """
    Возврат к выбору типа уведомлений.
    """

    data = await state.get_data()
    list_title = data.get("list_title", "")

    await callback.message.edit_text(
        text=f"✅ Список *{list_title}* создан!\n\n"
             "Выберите тип уведомлений:",
        reply_markup=get_notification_type_keyboard(),
        parse_mode="Markdown"
    )

    await state.set_state(ListStates.waiting_for_notification_type)
    await callback.answer()

@router.callback_query(ListStates.waiting_for_remind_decision, F.data.in_(["list_remind_yes", "list_remind_no"]))
async def process_remind_decision(callback: CallbackQuery, state: FSMContext, service: UserService):
    """Обработчик контекстного меню установки напоминания."""
    data = await state.get_data()
    user_message_id = data.get("user_message_id")

    # 🔥 удаляем сообщение бота с просьбой ввести название
    await delete_fsm_prompt_message(state=state, bot=callback.bot, chat_id=callback.message.chat.id)

    # 🔥 удаляем сообщение пользователя с названием списка (✔️ корректно)
    if user_message_id:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=user_message_id
            )
        except TelegramForbiddenError:
            pass

    if callback.data == "list_remind_no":

        await show_lists_view(callback=callback, service=service)

        await state.clear()
        return

    # если да — просим время
    edited_message = await callback.message.edit_text(
        text="Введите время напоминания в формате HH:MM (например 09:00)"
    )

    # сохраняем id сообщения бота с просьбой ввести время
    await state.update_data(remind_prompt_message_id=edited_message.message_id)

    await state.set_state(ListStates.waiting_for_remind_time)

# обработчик ввода времени
@router.message(ListStates.waiting_for_remind_time)
async def process_remind_time(
    message: Message,
    state: FSMContext,
    service: UserService,
    update_reminder_uc: UpdateListReminderSettingsUseCase
):
    """
    Обрабатывает ввод времени для уведомлений.
    """

    # ------------------ 1️⃣ Парсим время ------------------
    try:
        hours, minutes = map(int, message.text.split(":"))
        remind_time = time(hour=hours, minute=minutes)
    except ValueError:
        await _handle_time_error(message, state)
        return

    data = await state.get_data()

    list_id = data["list_id"]
    list_title = data["list_title"]
    notification_type = data["notification_type"]
    repeat_type = data["repeat_type"]
    week_days = data.get("week_days")
    chosen_dates = data.get("chosen_dates")

    await _cleanup_time_messages(message, data)

    # ------------------ 2️⃣ Формируем run_dates если ONCE ------------------
    run_dates = None

    if chosen_dates:
        run_dates = [
            datetime(
                year=int(date_str.split("-")[0]),
                month=int(date_str.split("-")[1]),
                day=int(date_str.split("-")[2]),
                hour=remind_time.hour,
                minute=remind_time.minute
            )
            for date_str in chosen_dates
        ]

        repeat_type = RepeatType.ONCE

    # ------------------ 3️⃣ Вызываем use case один раз ------------------
    try:
        task_list = await update_reminder_uc.execute(
            user_id=message.from_user.id,
            list_id=list_id,
            remind_time=remind_time,
            repeat_type=repeat_type,
            run_dates=run_dates,
            notification_type=notification_type,
            week_days=week_days
        )
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {e}")
        await state.clear()
        return

    # ------------------ 4️⃣ Отправляем подтверждение ------------------
    await _send_success_message(
        message=message,
        service=service,
        task_list=task_list,
        list_title=list_title,
        remind_time=remind_time,
        repeat_type=repeat_type,
        chosen_dates=chosen_dates,
        notification_type=notification_type
    )

    await state.clear()

# очистка времени
async def _handle_time_error(message: Message, state: FSMContext):
    try:
        await message.delete()
    except TelegramForbiddenError:
        pass

    error_msg = await message.answer(
        "❌ Неверный формат времени. Введите как HH:MM"
    )

    await state.update_data(remind_error_message_id=error_msg.message_id)

# очистка сообщений
async def _cleanup_time_messages(message: Message, data: dict):
    try:
        await message.delete()
    except TelegramForbiddenError:
        pass

    for key in ("remind_prompt_message_id", "time_prompt_message_id", "remind_error_message_id"):
        msg_id = data.get(key)
        if msg_id:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=msg_id
                )
            except Exception:
                pass

# сообщение об успехе
async def _send_success_message(
    message: Message,
    service: UserService,
    task_list,
    list_title: str,
    remind_time: time,
    repeat_type: RepeatType,
    chosen_dates: list | None,
    notification_type: NotificationType
):
    repeat_text = {
        RepeatType.DAILY: "ежедневно",
        RepeatType.WEEKDAYS: "по будням",
        RepeatType.WEEKENDS: "по выходным",
        RepeatType.ONCE: "выбранные даты",
        RepeatType.CUSTOM: "выбранные дни недели"
    }.get(repeat_type, "")

    notification_text = "📊 Опрос" if notification_type == NotificationType.POLL else "⏰ Напоминание"

    user = service.get_user_by_id(message.from_user.id)

    if chosen_dates:
        dates_text = ", ".join(sorted(chosen_dates))
        text = (
            f"✅ {notification_text} для списка *{list_title}* установлено!\n"
            f"🕐 Время: {remind_time.strftime('%H:%M')}\n"
            f"📅 Даты: {dates_text}"
        )
    else:
        text = (
            f"✅ {notification_text} для списка *{list_title}* установлено!\n"
            f"🕐 Время: {remind_time.strftime('%H:%M')}\n"
            f"🔁 Периодичность: {repeat_text}"
        )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_lists_keyboard(user.listoftasks)
    )

@router.callback_query(F.data == "list:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Отмена текущего действия (FSM)
    """
    await delete_fsm_prompt_message(state=state, bot=callback.bot, chat_id=callback.message.chat.id)

    await state.clear()

    await show_lists_view(callback=callback, service=service)

    await callback.answer(list_view.action_canceled)


@router.callback_query(F.data == "list:delete")
async def delete_list_start(callback: CallbackQuery, service: UserService):
    """Обработчик запуска процесса удаления списка."""
    user = service.get_user_by_id(callback.from_user.id)
    if not user.listoftasks:
        await callback.message.edit_text(list_view.no_lists)
        await callback.answer()
        return

    await callback.message.edit_text(text=list_view.list_delete_choice_prompt,
                                     reply_markup=get_lists_for_delete_keyboard(user.listoftasks)
                                     )
    await callback.answer()


@router.callback_query(F.data.startswith("list:confirm_delete:"))
async def confirm_delete(callback: CallbackQuery, service: UserService):
    """Обработчик контекстного окна подтверждения удаления списка."""
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    list_to_delete = service.get_list_by_id(callback.from_user.id, list_id)

    if not list_to_delete:
        await callback.answer("Список не найден", show_alert=True)
        return

    await callback.message.edit_text(text=list_view.confirm_delete_list(list_to_delete.title),
                                     reply_markup=get_confirm_delete_keyboard(list_id)
                                     )
    await callback.answer()


@router.callback_query(F.data.startswith("list:delete_yes:"))
async def delete_list_confirm(callback: CallbackQuery, service: UserService):
    """Обработчик подтверждения удаления списка."""
    _, _, list_id = callback.data.split(":")
    list_id = int(list_id)

    service.delete_list_of_tasks(callback.from_user.id, list_id)

    text = list_view.list_deleted_success

    await show_lists_view(callback=callback, service=service, prefix_text=text)
    await callback.answer(text=list_view.list_deleted_success)

#1 Дублируется логика с обработчиком снизу, проверить.  # noqa: RUF003
@router.callback_query(F.data.startswith("list:delete_no:"))
async def delete_list_cancel(callback: CallbackQuery, service: UserService):
    """Обработчик отмены удаления списка."""
    await show_lists_view(callback=callback, service=service)
    await callback.answer(text=list_view.delete_action_canceled)


@router.callback_query(F.data == "list:delete_cancel")
async def cancel_delete_start(callback: CallbackQuery, service: UserService):
    """Обработчик отмены удаления списка."""
    await show_lists_view(callback=callback, service=service)
    await callback.answer(text=list_view.delete_action_canceled)

@router.callback_query(lambda c: c.data == "menu:hide")
async def hide_menu(callback: CallbackQuery):
    """Обработчик скрытия (удаления) сообщения и клавиатуры со списком."""
    await callback.message.delete()
    await callback.answer("Меню скрыто 👌", show_alert=False)

