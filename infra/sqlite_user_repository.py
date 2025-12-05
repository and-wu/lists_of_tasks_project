import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from domain.users import User
from domain.interfaces.user_repository import IUserRepository


# =============================================
# Реализации SQL — ТОЛЬКО работа с данными, без создания таблиц!
# =============================================

class SqliteUserRepository(IUserRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute("SELECT id, name, username FROM users WHERE id = ?", (user_id,)).fetchone()
            return User.from_dict(
                id=row["id"],
                name=row["name"],
                username=row["username"],
                listoftasks=[]
            ) if row else None

    def get_by_username(self, username: str) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute("SELECT id, name, username FROM users WHERE username = ?", (username,)).fetchone()
            return User.from_dict(
                id=row["id"],
                name=row["name"],
                username=row["username"],
                listoftasks=[]
            ) if row else None

    def save(self, user: User) -> User:
        with self._conn() as conn:
            if user.id and self.get_by_id(user.id):
                conn.execute("UPDATE users SET name = ?, username = ? WHERE id = ?",
                             (user.name, user.username, user.id))
            else:
                cursor = conn.execute("INSERT INTO users (name, username) VALUES (?, ?)", (user.name, user.username))
                if not user.id:
                    user.id = cursor.lastrowid or 0

        return user

    def all(self) -> list[User]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, name, username FROM users").fetchall()
            return [User.from_dict(
                id=row["id"],
                name=row["name"],
                username=row["username"],
                listoftasks=[]
            ) for row in rows]

    def delete(self, user_id: int) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
