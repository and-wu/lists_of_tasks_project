from dataclasses import dataclass, field
from domain.task_list import ListOfTasks


# =============================================
# Модель
# =============================================


@dataclass
class User:
    id: int
    name: str
    username: str
    google_sheet_url: str | None = None
    listoftasks: list[ListOfTasks] = field(default_factory=list)

    def rename(self, new_name: str):
        if len(new_name) < 2:
            raise ValueError("Name is too short")
        self.name = new_name


    def to_dict(self) -> dict:
        return {"id": self.id,
                "name": self.name,
                "username": self.username,
                "google_sheet_url": self.google_sheet_url,
                "listoftasks": [ls.to_dict() for ls in self.listoftasks]
                }

    @classmethod
    def from_dict(cls, **data) -> "User":
        """
        Безопасно создаёт User из dict.
        Работает даже если каких-то полей нет.
        """

        raw_lists = data.get("listoftasks", [])
        lists = [ListOfTasks.from_dict(**lst) for lst in raw_lists]

        return cls(
            id=data["id"],
            name=data["name"],
            username=data.get("username"),
            google_sheet_url=data.get("google_sheet_url"),
            listoftasks=lists
        )
