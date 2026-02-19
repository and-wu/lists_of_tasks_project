from datetime import datetime, time, timedelta
from unittest.mock import sentinel

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from application.user.create_user import UserService
from domain.enums.notification_type import NotificationType
from presentation.telegram.keyboards.task_keyboards import get_tasks_keyboard
from presentation.telegram.states.list_states import ListStates
from presentation.telegram.keyboards.calendar_keyboard import get_calendar_keyboard
from presentation.telegram.keyboards.extra_keyboard import get_cancel_keyboard
from application.usecases.update_list_reminder_settings import UpdateListReminderSettingsUseCase
from domain.enums.repeat_type import RepeatType

router = Router()


# Выбор/снятие даты в календаре
@router.callback_query(ListStates.waiting_for_custom_dates, F.data.startswith("toggle_date"))
async def toggle_custom_date(callback: CallbackQuery, state: FSMContext):
    day_str = callback.data.split(":")[1]

    data = await state.get_data()
    selected_dates = set(data.get("selected_dates", []))
    year = data.get("calendar_year")
    month = data.get("calendar_month")

    # Создаем ISO-строку даты
    full_date = datetime(year, month, int(day_str)).date().isoformat()

    # Добавляем или убираем из выбранных
    if full_date in selected_dates:
        selected_dates.remove(full_date)
    else:
        selected_dates.add(full_date)

    await state.update_data(selected_dates=list(selected_dates))

    # Обновляем клавиатуру
    new_markup = get_calendar_keyboard(year, month, list(selected_dates))
    old_markup = callback.message.reply_markup

    if str(old_markup) != str(new_markup):
        try:
            await callback.message.edit_reply_markup(reply_markup=new_markup)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise

    await callback.answer()


# Листание месяцев
@router.callback_query(ListStates.waiting_for_custom_dates, F.data.in_(["prev_month", "next_month"]))
async def change_calendar_month(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    year = data.get("calendar_year")
    month = data.get("calendar_month")
    selected_dates = data.get("selected_dates", [])

    if callback.data == "prev_month":
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    else:
        month += 1
        if month > 12:
            month = 1
            year += 1

    await state.update_data(calendar_year=year, calendar_month=month)
    await callback.message.edit_reply_markup(
        reply_markup=get_calendar_keyboard(year, month, selected_dates)
    )
    await callback.answer()


# Подтверждение выбранных дат
@router.callback_query(
    ListStates.waiting_for_custom_dates,
    F.data == "confirm_dates"
)
async def confirm_custom_dates(
    callback: CallbackQuery,
    state: FSMContext,
    service: UserService,
    update_reminder_uc: UpdateListReminderSettingsUseCase,
):
    data = await state.get_data()
    selected_dates = sorted(data.get("selected_dates", []))

    if not selected_dates:
        await callback.answer("Выберите хотя бы одну дату!", show_alert=True)
        return

    list_id = data.get("list_id")
    user_id = callback.from_user.id

    task_list = service.get_list_by_id(user_id, list_id)

    # -----------------------------
    # Преобразуем даты в datetime
    # -----------------------------
    run_dates = [
        datetime.fromisoformat(date_str)
        for date_str in selected_dates
    ]

    # -----------------------------
    # Если время УЖЕ установлено
    # -----------------------------
    if task_list.remind_time is not None:

        # объединяем дату + уже существующее время
        run_dates_with_time = [
            dt.replace(
                hour=task_list.remind_time.hour,
                minute=task_list.remind_time.minute
            )
            for dt in run_dates
        ]

        updated_list = await update_reminder_uc.execute(
            user_id=user_id,
            list_id=list_id,
            remind_time=task_list.remind_time,
            repeat_type=RepeatType.ONCE,
            run_dates=run_dates_with_time,
            notification_type=task_list.notification_type,
            week_days=None,
        )

        dates_text = ", ".join(
            dt.strftime("%d.%m.%Y")
            for dt in run_dates_with_time
        )

        time_text = updated_list.remind_time.strftime("%H:%M")

        notification_icon = (
            "⏰ Напоминание"
            if updated_list.notification_type == NotificationType.REMINDER
            else "📊 Опрос"
        )

        text = (
            f"📋 *{updated_list.title}*\n\n"
            f"🔔 Тип: {notification_icon}\n"
            f"📆 Даты: {dates_text}\n"
            f"⏰ Время: {time_text}\n\n"
            f"✅ Даты обновлены!"
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=get_tasks_keyboard(tasks=task_list.tasks,
                                            list_id=list_id,
                                            tasks_list=task_list),
            parse_mode="Markdown"
        )

        await state.clear()
        await callback.answer()
        return

    # -----------------------------
    # Если времени НЕТ — просим ввести
    # -----------------------------
    await state.update_data(chosen_dates=selected_dates)

    sent_message = await callback.message.edit_text(
        f"Выбраны даты: {', '.join(selected_dates)}\n"
        f"⏰ Теперь введите время в формате HH:MM\n"
        f"Например: 20:00",
        reply_markup=get_cancel_keyboard("list")
    )

    await state.update_data(time_prompt_message_id=sent_message.message_id)
    await state.set_state(ListStates.waiting_for_remind_time)

    await callback.answer("Даты сохранены ✅")