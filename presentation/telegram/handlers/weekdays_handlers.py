from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from application.usecases.update_list_reminder_settings import UpdateListReminderSettingsUseCase
from domain.enums.repeat_type import RepeatType
from presentation.telegram.keyboards.extra_keyboard import get_cancel_keyboard
from presentation.telegram.keyboards.notification_repeat_keyboard import get_notification_type_keyboard, \
    get_repeat_type_keyboard
from presentation.telegram.keyboards.weekdays_keyboard import get_weekdays_keyboard
from presentation.telegram.states.list_states import ListStates

router = Router()

@router.callback_query(F.data.startswith("toggle_day"))
async def toggle_day(callback: CallbackQuery, state: FSMContext):
    day = int(callback.data.split(":")[1])

    data = await state.get_data()
    selected = set(data.get("selected_days", []))

    if day in selected:
        selected.remove(day)
    else:
        selected.add(day)

    await state.update_data(selected_days=list(selected))

    await callback.message.edit_reply_markup(
        reply_markup=get_weekdays_keyboard(list(selected))
    )

    await callback.answer()

@router.callback_query(F.data == "confirm_days")
async def confirm_days(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    if not selected_days:
        await callback.answer("Выберите хотя бы один день", show_alert=True)
        return

    # Сохраняем выбранные дни в FSM
    await state.update_data(week_days=selected_days)

    # Удаляем сообщение с клавиатурой дней недели
    try:
        await callback.message.delete()
    except Exception:
        pass

    # Переходим к вводу времени
    sent_message = await callback.message.answer(
        "⏰ Введите время в формате HH:MM\nНапример: 09:00",
        reply_markup=get_cancel_keyboard("list")
    )

    await state.update_data(time_prompt_message_id=sent_message.message_id)
    await state.set_state(ListStates.waiting_for_remind_time)
    await callback.answer("Выберите время напоминания")


@router.callback_query(F.data.startswith("back:"))
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Универсальная кнопка 'Назад' для всех FSM.
    """
    target_state = callback.data.split(":")[1]
    data = await state.get_data()

    # Чистим временные данные, связанные с кастомными днями
    if "selected_days" in data:
        data.pop("selected_days")
        await state.update_data(**data)

    if target_state == "repeat_type":
        list_title = data.get("list_title", "")
        await callback.message.edit_text(
            f"✅ Список *{list_title}* создан!\n\nВыберите периодичность напоминаний:",
            reply_markup=get_repeat_type_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(ListStates.waiting_for_repeat_type)

    elif target_state == "notification_type":
        list_title = data.get("list_title", "")
        await callback.message.edit_text(
            f"✅ Список *{list_title}* создан!\n\nВыберите тип уведомлений:",
            reply_markup=get_notification_type_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(ListStates.waiting_for_notification_type)

    await callback.answer("Вернулись назад ⬅️")