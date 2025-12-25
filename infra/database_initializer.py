import sqlite3
from pathlib import Path

# =============================================
# Отдельный сервис инициализации (миграции)
# =============================================

class DatabaseInitializer:
    @staticmethod
    def initialize_sqlite(db_path: Path) -> None:
        """Создаёт таблицу, если её ещё нет."""
        conn = sqlite3.connect(db_path.with_suffix(".db"))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def initialize_json(file_path: Path) -> None:
        """Просто создаёт пустой файл (или папку), если его нет."""
        file_path = file_path.with_suffix(".json")
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("{}", encoding="utf-8")
