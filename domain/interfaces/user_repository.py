from typing import Protocol, Optional, runtime_checkable

from domain.users import User


# =============================================
# Чистый интерфейс репозитория
# =============================================

@runtime_checkable
class IUserRepository(Protocol):
    def get_by_id(self, user_id: int) -> Optional[User]: ...
    def get_by_username(self, username: str) -> Optional[User]: ...
    def save(self, user: User) -> User: ...
    def all(self) -> list[User]: ...
    def delete(self, user_id: int) -> None: ...


