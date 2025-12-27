from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any

from domain.tasks import Task


@dataclass
class ListOfTasks:
    id: int
    title: str
    owner_id: int
    remind_time: time | None = None  # ⏰ время ежедневного показа
    tasks: list[Task] = field(default_factory=list)

    def add_task_to_list(self, task: Task) -> Task:
        self.tasks.append(task)
        return task

    def remove_task_from_list(self, task_for_remove: Task) -> None:
        self.tasks = [task for task in self.tasks if task.id != task_for_remove.id]

    def clear(self) -> None:
        self.tasks.clear()

    def get_task(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> list[Task] | None:
        return self.tasks

    def max_id(self) -> int:
        max_id = 0
        for task in self.tasks:
            max_id = max(task.id, max_id) + 1

        return max_id

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "owner_id": self.owner_id,
            "remind_time": self.remind_time.strftime("%H:%M")
            if self.remind_time
            else None,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(
        cls,
        id: int,
        title: str,
        owner_id: int,
        tasks: list[dict[str, str]],
        remind_time: str | None = None,
        **kwargs: dict[str, Any],
    ) -> "ListOfTasks":
        tasks_obj = [Task.from_dict(**t) for t in tasks]

        parsed_remind_time: time | None = (
            datetime.strptime(remind_time, "%H:%M").time() if remind_time else None
        )
        return cls(
            id=id,
            title=title,
            owner_id=owner_id,
            tasks=tasks_obj,
            remind_time=parsed_remind_time,
        )
