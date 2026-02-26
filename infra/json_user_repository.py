import json
from pathlib import Path

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
            with open(self.file_path, encoding="utf-8") as f:
                raw = json.load(f)
                return {
                    int(user_id): User.from_dict(**user_data)
                    for user_id, user_data in raw.items()
                }
                #return {int(k): User.from_dict(**v) for k, v in raw.items()}
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

    def delete_list(self, user_id: int, list_id: int) -> bool:
        """
        Удаляет список пользователя по ID.
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

    def delete_task(self, user_id: int, task_id: int) -> None:
        """
            Удаляет задачу пользователя по task_id.
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

    def reset_all_tasks_test(self) -> None:
        """
        Сбросить completed у всех задач всех пользователей
        """
        #user = self.get_by_id(user_id)
        for user in self._data.values():
            for list_of_task in user.listoftasks:
                for task in list_of_task.tasks:
                    task.completed = False

        self._save()
        print("Все задачи сброшены")

    def reset_all_tasks(self) -> dict[int, list[dict]]:
        """
        Сбрасывает и возвращает данные только по спискам,
        у которых был активный poll.
        """
        print("one")
        result: dict[int, list[dict]] = {}

        for user_id, user in self._data.items():
            user_rows = []

            for task_list in user.listoftasks:

                # ✅ Сбрасываем только если poll есть и пользователь проголосовал
                if not (task_list.active_poll_id and task_list.poll_voted):
                    continue

                for task in task_list.tasks:
                    user_rows.append({
                        "username": user.username,
                        "list_title": task_list.title,
                        "task": task.value,
                        "completed": task.completed
                    })

                    # 🔄 Сбрасываем статус задачи
                    task.completed = False

                # 🔥 Сбрасываем состояние poll
                task_list.poll_voted = False
                task_list.active_poll_id = None
                task_list.active_poll_message_id = None
                task_list.active_poll_task_ids.clear()

            if user_rows:
                result[user_id] = user_rows

        print("two")
        self._save()
        return result
