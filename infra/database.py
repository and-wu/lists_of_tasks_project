import json
from domain.task_list import ListOfTasks
from domain.tasks import Task
from domain.users import User


class Database:
    def __init__(self, path):
        self.path = path

    def mapping(self, data: dict):
        result = []
        for user in data:
            result.append(User.from_dict(**user))

        return result

        return result

    def demapping(self, data: list[User]):
        result = []
        for user in data:
            result.append(user.to_dict())

        return result

    def read(self, use_mapping=True):

        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if use_mapping:
            data = self.mapping(data)

        return data

    def save(self, data):
        data = self.demapping(data)

        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # записывает нового user'а в json
    def save_user(self, user: User) -> bool:

        data = self.read()
        data['users'].append({"id": user.id, "name": user.name, "listoftasks": user.listoftasks})

        with (open(self.path, 'w', encoding='utf-8') as f):
            try:
                json.dump(data, f, indent=4, ensure_ascii=False)
                print(f'в {self.path} добавили нового user {user.name}')
                return True
            except Exception as e:
                print(e)
                return False
