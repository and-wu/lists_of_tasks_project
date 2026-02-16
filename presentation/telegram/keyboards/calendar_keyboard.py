from calendar import monthrange
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- Календарь с месяцами ---
def get_calendar_keyboard(year: int, month: int, selected_dates: list[str] | None = None):
    selected_dates = selected_dates or []

    buttons = []
    row = []

    # Название месяца в шапке
    header = [InlineKeyboardButton(text=f"{year}-{month:02d}", callback_data="ignore")]
    buttons.append(header)

    # Дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons.append([InlineKeyboardButton(text=d, callback_data="ignore") for d in week_days])

    # Получаем первый день и количество дней в месяце
    first_weekday, days_in_month = monthrange(year, month)

    # Добавляем пустые кнопки для смещения
    for _ in range(first_weekday):  # в python понедельник=0
        row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day in range(1, days_in_month + 1):
        # создаем ISO-дату для этого дня
        full_date = datetime(year, month, day).date().isoformat()
        prefix = "✅ " if full_date in selected_dates else ""
        row.append(InlineKeyboardButton(text=f"{prefix}{day}", callback_data=f"toggle_date:{day}"))
        if len(row) == 7:
            buttons.append(row)
            row = []

    if row:
        # заполняем до 7
        while len(row) < 7:
            row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        buttons.append(row)

    # Навигация по месяцам + подтверждение/отмена
    buttons.append([
        InlineKeyboardButton(text="⬅", callback_data="prev_month"),
        InlineKeyboardButton(text="✔ Готово", callback_data="confirm_dates"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_dates"),
        InlineKeyboardButton(text="➡", callback_data="next_month")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)