from dataclasses import dataclass, field

from domain.task_list import ListOfTasks


@dataclass
class User:
    id: int
    name: str
    listoftasks: list[ListOfTasks] = field(default_factory=list)

    def rename(self, new_name: str):
        if len(new_name) < 2:
            raise ValueError("Name is too short")
        self.name = new_name


    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "listoftasks": [ls.to_dict() for ls in self.listoftasks]}


    @classmethod
    def from_dict(cls, id, name, listoftasks, **kwargs) -> "User":
        listoftasks_obj = [ListOfTasks.from_dict(**l) for l in listoftasks]
        return cls(id=id, name=name, listoftasks=listoftasks_obj)
