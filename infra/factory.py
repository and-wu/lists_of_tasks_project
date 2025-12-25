from pathlib import Path

from domain.interfaces.user_repository import IUserRepository
from infra.database_initializer import DatabaseInitializer
from infra.json_user_repository import JsonUserRepository
from infra.sqlite_user_repository import SqliteUserRepository

# =============================================
# Фабрика — единый интерфейс
# =============================================

class DBType:
    SQLITE = "sqlite"
    JSON = "json"


def create_repository(db_type: str, path: Path) -> IUserRepository:
    if db_type == DBType.SQLITE:
        path = path.with_suffix(".db")
        DatabaseInitializer.initialize_sqlite(path)
        return SqliteUserRepository(path)
    if db_type == DBType.JSON:
        path = path.with_suffix(".json")
        DatabaseInitializer.initialize_json(path)
        return JsonUserRepository(path)
    msg = f"Unknown db_type: {db_type}"
    raise ValueError(msg)
