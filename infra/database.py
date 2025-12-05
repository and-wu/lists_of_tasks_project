import json
from domain.users import User

import sqlite3
from contextlib import contextmanager
from pathlib import Path


class DataBase:
    def __init__(self, path: str):
        self.path = path

    @contextmanager
    def get_cursor(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            conn.close()

    def create_tasks_table(self):
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value TEXT NOT NULL,
                    description TEXT,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    task_list_id INTEGER NOT NULL,
                    FOREIGN KEY (task_list_id) REFERENCES task_lists(id)
                )
            """)

def get_database(path: Path) -> DataBase:
    return DataBase(path.as_posix())




exit()

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
