from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DAY_LABELS = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс",
}

def get_weekdays_keyboard(selected_days: list[int] | None = None):
    selected_days = selected_days or []

    buttons = []
    row = []

    for day in range(7):
        prefix = "✅ " if day in selected_days else ""
        row.append(
            InlineKeyboardButton(
                text=f"{prefix}{DAY_LABELS[day]}",
                callback_data=f"toggle_day:{day}"
            )
        )

        if len(row) == 4:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text="✔ Готово", callback_data="confirm_days")
    ])

    # 🔥 Кнопка отмены
    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="back:repeat_type")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)