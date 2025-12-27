import json
from pathlib import Path

from domain.interfaces.user_repository import IUserRepository
from domain.users import User


class JsonUserRepository(IUserRepository):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self._data = self._load()

    def _load(self) -> dict[int, User]:
        if not self.file_path.exists():
            return {}
        try:
            with open(self.file_path, encoding="utf-8") as f:
                raw = json.load(f)
                return {int(k): User.from_dict(**v) for k, v in raw.items()}
        except json.JSONDecodeError:
            return {}

    def _save(self) -> None:
        raw = {str(uid): user.to_dict() for uid, user in self._data.items()}
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)

    def _next_id(self) -> int:
        return max(self._data.keys(), default=0) + 1

    def get_by_id(self, user_id: int) -> User | None:
        return self._data.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        for user in self._data.values():
            if user.username == username:
                return user
        return None

    def save(self, user: User) -> User:
        self._data[user.id] = user
        self._save()

        return user

    def all(self) -> list[User]:
        return list(self._data.values())

    def delete(self, user_id: int) -> None:
        self._data.pop(user_id, None)
        self._save()

    def delete_list(self, user_id: int, list_id: int) -> bool:
        """Удаляет список пользователя по ID.

        Возвращает True, если список найден и удалён, иначе False.
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        # удаляем список из списка списков
        for i, lst in enumerate(user.listoftasks):
            if lst.id == list_id:
                user.listoftasks.pop(i)
                self._save()
                return True

        return False

    def delete_task(self, user_id: int, task_id: int) -> bool:
        """Удаляет задачу пользователя по task_id.

        Возвращает True, если задача найдена и удалён, иначе False.
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        # удаляем список из списка списков
        for list_of_task in user.listoftasks:
            for i, task in enumerate(list_of_task.tasks):
                if task.id == task_id:
                    list_of_task.tasks.pop(i)
                    self._save()
                    return True

        return False
