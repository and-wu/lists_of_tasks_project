from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_SQLite.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    value: Mapped[str] = mapped_column(String, default="", nullable=False)

    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # связь с ListOfTasks (TaskList)
    task_list_id: Mapped[int] = mapped_column(ForeignKey("list_of_tasks.id"))

    task_list: Mapped["ListOfTasks"] = relationship(back_populates="tasks")

    def complete(self):
        self.completed = True

    def rename(self, new_name: str):
        if len(new_name) < 2:
            raise ValueError("Task name too short")
        self.name = new_name