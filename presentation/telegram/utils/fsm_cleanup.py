from aiogram.exceptions import TelegramForbiddenError
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
    except TelegramForbiddenError:
        pass