from datetime import time
from typing import Optional

from sqlalchemy import String, ForeignKey, Time, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_SQLite.db import Base
from domain.SQLite_models.tasks import Task
from domain.enums.repeat_type import RepeatType


class ListOfTasks(Base):
    __tablename__ = "list_of_tasks"

    # ==========================================================
    # ---------------------- DB FIELDS --------------------------
    # ==========================================================

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # связь с User
    user: Mapped["User"] = relationship(back_populates="listoftasks")

    # -------------------------
    # 🔕 reminder settings
    # -------------------------

    remind_time: Mapped[str | None] = mapped_column(Time, nullable=True)
    repeat_type: Mapped[str | None] = mapped_column(String, nullable=True)
    notification_type: Mapped[str | None] = mapped_column(String, nullable=True)

    # списки и сложные структуры → JSON
    run_dates: Mapped[list | None] = mapped_column(JSON, nullable=True)
    week_days: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)

    # -------------------------
    # 📌 tasks внутри списка
    # -------------------------
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="task_list",
        cascade="all, delete-orphan"
    )

    # -------------------------
    # 🔥 POLL STATE (Telegram state)
    # -------------------------

    active_poll_id: Mapped[str | None] = mapped_column(String, nullable=True)
    active_poll_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_poll_task_ids: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    poll_voted: Mapped[bool] = mapped_column(Boolean, default=False)

    # ==========================================================
    # ---------------------- TASK LOGIC -------------------------
    # ==========================================================

    def add_task_to_list(self, task: Task) -> Task:
        self.tasks.append(task)
        return task

    def remove_task_from_list(self, task_for_remove: Task):
        if task_for_remove in self.tasks:
            self.tasks.remove(task_for_remove)

    def clear(self):
        self.tasks.clear()

    def get_task(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> list[Task]:
        return self.tasks

    # ==========================================================
    # -------------------- REMINDER LOGIC -----------------------
    # ==========================================================

    def has_reminder(self) -> bool:
        return self.remind_time is not None and self.repeat_type is not None

    def is_one_time(self) -> bool:
        return self.repeat_type == RepeatType.ONCE.value

    def is_valid_reminder(self) -> bool:
        if not self.has_reminder():
            return False

        if self.repeat_type == RepeatType.ONCE.value:
            return bool(self.run_dates)

        if self.repeat_type == RepeatType.CUSTOM.value:
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

        if self.repeat_type == RepeatType.DAILY.value:
            return "*"

        if self.repeat_type == RepeatType.WEEKDAYS.value:
            return "mon-fri"

        if self.repeat_type == RepeatType.WEEKENDS.value:
            return "sat,sun"

        if self.repeat_type == RepeatType.CUSTOM.value and self.week_days:
            day_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            return ",".join(day_map[d] for d in sorted(self.week_days))

        return None

    # ==========================================================
    # ---------------------- POLL LOGIC -------------------------
    # ==========================================================

    def is_poll_active(self) -> bool:
        return self.active_poll_id is not None

    def activate_poll(self, poll_id: str, message_id: int, task_ids: list[int]):

        self.active_poll_id = poll_id
        self.active_poll_message_id = message_id
        self.active_poll_task_ids = task_ids
        self.poll_voted = False

    def clear_poll(self):
        self.active_poll_id = None
        self.active_poll_message_id = None
        self.active_poll_task_ids = []
        self.poll_voted = False


