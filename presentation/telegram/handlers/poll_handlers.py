from aiogram import Router
from aiogram.types import PollAnswer

from application.poll.daily_poll_service import DailyPollService

router = Router()


@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, poll_service: DailyPollService):
    poll_id = poll_answer.poll_id
    selected_options = poll_answer.option_ids

    poll_data = poll_service.poll_map.get(poll_id)
    if not poll_data:
        return

    user_id = poll_data["user_id"]
    task_ids = poll_data["task_ids"]

    user = poll_service.user_service.get_user_by_id(user_id)

    # 🧠 Проставляем completed по индексам
    for idx, task_id in enumerate(task_ids):
        task = next(
            t
            for l in user.listoftasks
            for t in l.tasks
            if t.id == task_id
        )
        task.completed = idx in selected_options

    poll_service.user_service.save_user(user_id)
