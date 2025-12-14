import json
from pathlib import Path
from typing import Generator, Optional

from domain.users import User
from domain.interfaces.user_repository import IUserRepository


# =============================================
# Реализации JSON — ТОЛЬКО работа с данными, без создания таблиц!
# =============================================


class JsonUserRepository(IUserRepository):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._data = self._load()

    def _load(self) -> dict[int, User]:
        if not self.file_path.exists():
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                print(raw)
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

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._data.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        for user in self._data.values():
            if user.username == username:
                return user
        return None

    def save(self, user: User) -> User:
        #if user.id <= 0 or user.id not in self._data:
        #    user.id = self._next_id()
        self._data[user.id] = user
        self._save()

        return user

    def all(self) -> list[User]:
        return list(self._data.values())

    def delete(self, user_id: int) -> None:
        self._data.pop(user_id, None)
        self._save()
