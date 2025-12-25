from dataclasses import dataclass

# =============================================
# Модель
# =============================================

@dataclass
class Task:
    id: int
    value: str = ""
    completed: bool = False

    def complete(self) -> None:
        self.completed = True

    def rename(self, new_name: str) -> None:
        if len(new_name) < 2:
            msg = "Task name too short"
            raise ValueError(msg)
        self.name = new_name


    def to_dict(self) -> dict:
        return {"id": self.id, "value": self.value, "completed": self.completed}

    @classmethod
    def from_dict(cls, id, value, completed) -> "Task":
        return cls(id=id, value=value, completed=completed)
