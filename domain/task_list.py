from dataclasses import dataclass, field
from datetime import time, datetime
from typing import Optional

from domain.enums.notification_type import NotificationType
from domain.enums.repeat_type import RepeatType
from domain.tasks import Task

# =============================================
# Модель
# =============================================

@dataclass
class ListOfTasks:
    id: int
    title: str
    owner_id: int

    # 🔕 напоминание может отсутствовать
    remind_time: time | None = None # ⏰ время показа
    repeat_type: RepeatType | None = None
    run_dates: list[datetime] | None = None
    notification_type: NotificationType | None = None
    week_days: list[int] | None = None

    tasks: list[Task] = field(default_factory=list)

    # 🔥 POLL STATE (устойчивый к перезапуску)
    active_poll_id: Optional[str] = None
    active_poll_message_id: Optional[int] = None
    active_poll_task_ids: list[int] = field(default_factory=list)
    poll_voted: bool = False

    # ==========================================================
    # ---------------------- DOMAIN LOGIC ----------------------
    # ==========================================================

    # ---------------- Tasks ----------------

    def add_task_to_list(self, task: Task) -> Task:
        self.tasks.append(task)
        return task

    def remove_task_from_list(self, task_for_remove: Task):
        self.tasks = [task for task in self.tasks if task.id != task_for_remove.id]

    def clear(self):
        self.tasks.clear()

    def get_task(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> list[Task]:
        return self.tasks

    def max_id(self):
        max_id = 0
        for task in self.tasks:
            max_id = max(task.id, max_id) + 1
        return max_id

    # ---------------- Reminder ----------------

    def has_reminder(self) -> bool:
        return self.remind_time is not None and self.repeat_type is not None

    def is_one_time(self) -> bool:
        return self.repeat_type == RepeatType.ONCE

    def is_valid_reminder(self) -> bool:
        if not self.has_reminder():
            return False

        if self.repeat_type == RepeatType.ONCE:
            return bool(self.run_dates)

        if self.repeat_type == RepeatType.CUSTOM:
            return bool(self.week_days)

        return True

    def set_repeat_type(self, repeat_type: RepeatType):
        """
        Устанавливает новый repeat_type и корректно очищает
        run_dates / week_days в зависимости от выбранного типа.
        """
        self.repeat_type = repeat_type

        if repeat_type in (RepeatType.DAILY, RepeatType.WEEKDAYS, RepeatType.WEEKENDS):
            # Ежедневно, только будни, только выходные — run_dates и week_days не нужны
            self.run_dates = None
            self.week_days = None

        elif repeat_type == RepeatType.ONCE:
            # Один или несколько раз — week_days не нужен
            self.week_days = None

        elif repeat_type == RepeatType.CUSTOM:
            # Пользователь сам выбирает дни недели — run_dates не нужен
            self.run_dates = None

    def get_day_of_week_expression(self) -> str | None:
        if not self.repeat_type:
            return None

        if self.repeat_type == RepeatType.DAILY:
            return "*"

        if self.repeat_type == RepeatType.WEEKDAYS:
            return "mon-fri"

        if self.repeat_type == RepeatType.WEEKENDS:
            return "sat,sun"

        if self.repeat_type == RepeatType.CUSTOM and self.week_days:
            day_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            return ",".join(day_map[d] for d in sorted(self.week_days))

        return None

    # ---------------- Poll ----------------

    def is_poll_active(self) -> bool:
        return self.active_poll_id is not None

    def activate_poll(
            self,
            poll_id: str,
            message_id: int,
            task_ids: list[int]
    ):
        self.active_poll_id = poll_id
        self.active_poll_message_id = message_id
        self.active_poll_task_ids = task_ids
        self.poll_voted = False

    def clear_poll(self):
        self.active_poll_id = None
        self.active_poll_message_id = None
        self.active_poll_task_ids.clear()
        self.poll_voted = False

    # ==========================================================
    # --------------------- SERIALIZATION ----------------------
    # ==========================================================

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "owner_id": self.owner_id,
            "remind_time": self.remind_time.strftime("%H:%M") if self.remind_time else None,
            "repeat_type": self.repeat_type.value if self.repeat_type else None,
            "run_dates": [dt.isoformat() for dt in self.run_dates] if self.run_dates else None,
            "notification_type": self.notification_type.value if self.notification_type else None,
            "week_days": self.week_days,
            "tasks": [task.to_dict() for task in self.tasks],
            "active_poll_id": self.active_poll_id,
            "active_poll_message_id": self.active_poll_message_id,
            "active_poll_task_ids": self.active_poll_task_ids,
            "poll_voted": self.poll_voted,
        }

    @classmethod
    def from_dict(
            cls,
            id,
            title,
            owner_id,
            tasks,
            remind_time: str | None = None,
            repeat_type: str | None = None,
            run_dates: list[str] | None = None,
            notification_type: str | None = None,
            week_days: list[int] | None = None,
            active_poll_id: str | None = None,
            active_poll_message_id: int | None = None,
            active_poll_task_ids: list[int] | None = None,
            poll_voted: bool = False,
            **kwargs
    ) -> "ListOfTasks":

        tasks_obj = [Task.from_dict(**t) for t in tasks]

        parsed_remind_time = (
            datetime.strptime(remind_time, "%H:%M").time()
            if remind_time
            else None
        )

        parsed_repeat_type = RepeatType(repeat_type) if repeat_type else None

        parsed_run_dates = (
            [datetime.fromisoformat(dt_str) for dt_str in run_dates]
            if run_dates
            else None
        )

        parsed_notification_type = (
            NotificationType(notification_type)
            if notification_type
            else None
        )

        parsed_week_days = sorted(week_days) if week_days else None

        return cls(
            id=id,
            title=title,
            owner_id=owner_id,
            tasks=tasks_obj,
            remind_time=parsed_remind_time,
            repeat_type=parsed_repeat_type,
            run_dates=parsed_run_dates,
            notification_type=parsed_notification_type,
            week_days=parsed_week_days,
            active_poll_id=active_poll_id,
            active_poll_message_id=active_poll_message_id,
            active_poll_task_ids=active_poll_task_ids or [],
            poll_voted=poll_voted
        )



    # # 🔥 временно: poll текущего дня
    # active_poll_id: str | None = None
    # poll_voted: bool = False  # ✅ пользователь ответил на опрос
    #
    #
    #
    #
    # # --- Domian Logic ---
    #
    # def add_task_to_list(self, task: Task) -> Task:
    #     self.tasks.append(task)
    #     return task
    #
    # def remove_task_from_list(self, task_for_remove: Task):
    #     self.tasks = [task for task in self.tasks if task.id != task_for_remove.id]
    #
    # def clear(self):
    #     self.tasks.clear()
    #
    # def get_task(self, task_id: int) -> Task | None:
    #     for task in self.tasks:
    #         if task.id == task_id:
    #             return task
    #     return None
    #
    # def get_all_tasks(self) -> list[Task] | None:
    #     return self.tasks
    #
    #
    # def max_id(self):
    #     max_id = 0
    #     for task in self.tasks:
    #         max_id = max(task.id, max_id) + 1
    #
    #     return max_id
    #
    # def has_reminder(self) -> bool:
    #     return self.remind_time is not None and self.repeat_type is not None
    #
    # def is_one_time(self) -> bool:
    #     return self.repeat_type == RepeatType.ONCE
    #
    # def is_valid_reminder(self) -> bool:
    #     if not self.has_reminder():
    #         return False
    #
    #     if self.repeat_type == RepeatType.ONCE:
    #         return self.run_dates is not None
    #
    #     if self.repeat_type == RepeatType.CUSTOM:
    #         return bool(self.week_days)
    #
    #     return True
    #
    # def get_day_of_week_expression(self) -> str | None:
    #     if not self.repeat_type:
    #         return None
    #
    #     if self.repeat_type == RepeatType.DAILY:
    #         return "*"
    #
    #     if self.repeat_type == RepeatType.WEEKDAYS:
    #         return "mon-fri"
    #
    #     if self.repeat_type == RepeatType.WEEKENDS:
    #         return "sat,sun"
    #
    #     if self.repeat_type == RepeatType.CUSTOM and self.week_days:
    #         day_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    #         return ",".join(day_map[d] for d in sorted(self.week_days))
    #
    #     return None
    #
    # def to_dict(self) -> dict:
    #     return {"id": self.id,
    #             "title": self.title,
    #             "owner_id": self.owner_id,
    #             "remind_time": self.remind_time.strftime("%H:%M") if self.remind_time else None,
    #             "repeat_type": self.repeat_type.value if self.repeat_type else None,
    #             "run_dates": [dt.isoformat() for dt in self.run_dates] if self.run_dates else None,
    #             "notification_type": self.notification_type.value if self.notification_type else None,
    #             "week_days": self.week_days,
    #             "tasks": [task.to_dict() for task in self.tasks],
    #             "active_poll_id": self.active_poll_id,
    #             "poll_voted": self.poll_voted}
    #
    # @classmethod
    # def from_dict(cls,
    #               id,
    #               title,
    #               owner_id,
    #               tasks,
    #               remind_time: str | None = None,
    #               repeat_type: str | None = None,
    #               run_dates: list[str] | None = None,
    #               notification_type: str | None = None,
    #               week_days: list[int] | None = None,
    #               active_poll_id: str | None = None ,
    #               poll_voted: bool = False,
    #               **kwargs) -> "ListOfTasks":
    #
    #     tasks_obj = [Task.from_dict(**t) for t in tasks]
    #
    #     parsed_remind_time: time | None = (
    #         datetime.strptime(remind_time, "%H:%M").time()
    #         if remind_time
    #         else None
    #     )
    #
    #     parsed_repeat_type = (
    #         RepeatType(repeat_type)
    #         if repeat_type
    #         else None
    #     )
    #
    #     parsed_run_dates: list[datetime] | None = (
    #         [datetime.fromisoformat(dt_str) for dt_str in run_dates]
    #         if run_dates
    #         else None
    #     )
    #
    #     parser_notification_type = (
    #         NotificationType(notification_type)
    #         if notification_type
    #         else None
    #     )
    #
    #     parsed_week_days: list[int] | None = (
    #         sorted(week_days)
    #         if week_days
    #         else None
    #     )
    #
    #     return cls(
    #         id=id,
    #         title=title,
    #         owner_id=owner_id,
    #         tasks=tasks_obj,
    #         remind_time=parsed_remind_time,
    #         repeat_type=parsed_repeat_type,
    #         run_dates=parsed_run_dates,
    #         notification_type=parser_notification_type,
    #         week_days=parsed_week_days,
    #         active_poll_id=active_poll_id,
    #         poll_voted=poll_voted
    #     )
