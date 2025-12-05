from pathlib import Path

from application.user.create_user import UserService
from infra.factory import create_repository, DBType
from presentation.cli.cli import CLI

repo = create_repository(
    db_type=DBType.JSON,  # DBType.JSON или DBType.SQLITE
    path=Path("storage/users"))

service = UserService(repo=repo)

cli = CLI(user_service=service)

cli.run()



