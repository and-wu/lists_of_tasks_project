from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext


async def delete_fsm_prompt_message(state: FSMContext, bot, chat_id: int):
    """Вспомогательная функция для удаления сообщения."""
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if not prompt_message_id:
        return

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=prompt_message_id
        )
    except TelegramBadRequest:
        # сообщение уже удалено — это НЕ ошибка
        pass

        # 🔥 ВАЖНО: очищаем prompt из FSM
    await state.update_data(prompt_message_id=None)