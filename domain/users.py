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
    listoftasks: list[ListOfTasks] = field(default_factory=list)

    def rename(self, new_name: str) -> None:
        if len(new_name) < 2:
            msg = "Name is too short"
            raise ValueError(msg)
        self.name = new_name


    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "username": self.username, "listoftasks": [ls.to_dict() for ls in self.listoftasks]}


    @classmethod
    def from_dict(cls, id, name, username, listoftasks, **kwargs) -> "User":
        #listoftasks = listoftasks or []
        listoftasks_obj = [ListOfTasks.from_dict(**l) for l in listoftasks]
        return cls(id=id, name=name, username=username, listoftasks=listoftasks_obj)
