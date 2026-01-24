from datetime import date

from aiogram import Bot

class DailyPollService:
    def __init__(self, bot: Bot, user_service):
        self.bot = bot
        self.user_service = user_service

        # poll_id -> [task_id]
        self.poll_map: dict[str, dict] = {}

    async def send_daily_poll(self, user_id: int, list_id: int):
        user = self.user_service.get_user_by_id(user_id)
        listoftasks = next(l for l in user.listoftasks if l.id == list_id)

        if not listoftasks.tasks:
            return

        # ⚠️ максимум 10 задач
        tasks = listoftasks.tasks[:10]

        options = [task.value for task in tasks]

        today = date.today().strftime("%d.%m.%Y")

        poll_msg = await self.bot.send_poll(
            chat_id=user_id,
            question= (f"📅 {today}\n\n"
                       f"🕒 {listoftasks.title}"),
            options=options,
            allows_multiple_answers=True,
            is_anonymous=False
        )

        poll_id = poll_msg.poll.id

        # 🔗 СОХРАНЯЕМ ПОЛНУЮ СВЯЗЬ
        self.poll_map[poll_id] = {
            "user_id": user_id,
            "list_id": list_id,
            "task_ids": [task.id for task in tasks]
        }

        # сохраняем poll в списке
        listoftasks.active_poll_id = poll_id
        self.user_service.save_user(user_id)
