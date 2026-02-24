from aiogram import Router
from aiogram.types import PollAnswer

from application.poll.daily_poll_service import DailyPollService

router = Router()

@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, poll_service: DailyPollService):
    poll_id = poll_answer.poll_id
    selected_options = poll_answer.option_ids

    # получаем пользователя
    user = poll_service.user_service.get_user_by_id(poll_answer.user.id)
    if not user:
        return

    # находим список с активным poll
    task_list = next(
        (l for l in user.listoftasks if l.active_poll_id == poll_id),
        None
    )
    if not task_list:
        return

    # ставим completed для задач по выбранным индексам
    for idx, task_id in enumerate(task_list.active_poll_task_ids):
        task = next((t for t in task_list.tasks if t.id == task_id), None)
        if task:
            task.completed = idx in selected_options

    # фиксируем факт голосования
    task_list.poll_voted = True

    # сохраняем изменения
    poll_service.user_service.save_user(user.id)