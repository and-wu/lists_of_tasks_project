from pathlib import Path

from application.user.create_user import UserService
from infra.factory import create_repository, DBType

repo = create_repository(
    db_type=DBType.SQLITE,  # DBType.JSON или DBType.SQLITE
    path=Path("storage/users"))

service = UserService(repo=repo)


service.