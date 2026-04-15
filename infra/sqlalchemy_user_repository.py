from sqlalchemy.orm import selectinload

from domain.SQLite_models.tasks_list import ListOfTasks
from domain.SQLite_models.users import User
from domain.interfaces.user_repository import IUserRepository


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    # -------------------------
    # GET
    # -------------------------

    def get_by_id(self, user_id: int) -> User | None:
        with self.session_factory() as session:
            return (
                session.query(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
                .filter(User.id == user_id)
                .first()
            )

    def get_by_username(self, username: str) -> User | None:
        with self.session_factory() as session:
            return (
                session.query(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
                .filter(User.username == username)
                .first()
            )

    # -------------------------
    # SAVE
    # -------------------------

    def save(self, user: User) -> User:
        with self.session_factory() as session:
            session.add(user)
            session.commit()
            session.refresh(user)  # чтобы получить id после insert
            return user

    # -------------------------
    # ALL
    # -------------------------

    def all(self) -> list[User]:
        with self.session_factory() as session:
            return (
                session.query(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
                .all()
            )

    # -------------------------
    # DELETE
    # -------------------------

    def delete(self, user_id: int) -> None:
        with self.session_factory() as session:
            user = (
                session.query(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
                .filter(User.id == user_id)
                .first()
            )
            if user:
                session.delete(user)
                session.commit()