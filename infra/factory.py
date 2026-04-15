from pathlib import Path

from db_SQLite.init_db import init_db
from db_SQLite.db import SessionLocal
from domain.interfaces.user_repository import IUserRepository
from infra.database_initializer import DatabaseInitializer
from infra.json_user_repository import JsonUserRepository
from infra.sqlalchemy_user_repository import SQLAlchemyUserRepository


# =============================================
# Фабрика — единый интерфейс
# =============================================

class DBType:
    SQLITE = "sqlite"
    JSON = "json"


def create_repository(db_type: str, path: Path) -> IUserRepository:
    if db_type == DBType.SQLITE:
        path = path.with_suffix(".db")

        init_db()  # ✅ СОЗДАНИЕ ТАБЛИЦ (ВАЖНО: ДО РЕПОЗИТОРИЕВ)

        return SQLAlchemyUserRepository(SessionLocal)

    elif db_type == DBType.JSON:
        # Если путь уже заканчивается на .json, не добавляем лишнее
        if path.suffix != ".json":
            path = path.with_suffix(".json")

        # Создаём файл, если его нет
        DatabaseInitializer.initialize_json(path)

        return JsonUserRepository(path)
    else:
        raise ValueError(f"Unknown db_type: {db_type}")
