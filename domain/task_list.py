from dataclasses import dataclass, field
from uuid import UUID

from domain.tasks import Task

# =============================================
# Модель
# =============================================

@dataclass
class ListOfTasks:
    id: int
    title: str
    owner_id: int
    tasks: list[Task] = field(default_factory=list)

    # --- Domian Logic ---

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

    def max_id(self):
        max_id = 0
        for task in self.tasks:
            max_id = max(task.id, max_id) + 1

        return max_id

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "owner_id": self.owner_id,
                "tasks": [task.to_dict() for task in self.tasks]}

    @classmethod
    def from_dict(cls, id, title, owner_id, tasks, **kwargs) -> "ListOfTasks":
        tasks_obj = [Task.from_dict(**t) for t in tasks]
        return cls(id=id, title=title, owner_id=owner_id, tasks=tasks_obj)
