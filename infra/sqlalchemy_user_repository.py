from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.SQLite_models.users import User
from domain.SQLite_models.tasks_list import ListOfTasks
from domain.SQLite_models.tasks import Task
from domain.interfaces.user_repository import IUserRepository


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    # =========================
    # INTERNAL QUERY BUILDER
    # =========================

    def _base_query(self):
        return (
            select(User)
            .options(
                selectinload(User.listoftasks)
                .selectinload(ListOfTasks.tasks)
            )
        )

    # =========================
    # GET
    # =========================

    def get_by_id(self, user_id: int) -> User | None:
        with self.session_factory() as session:
            stmt = self._base_query().where(User.id == user_id)
            return session.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        with self.session_factory() as session:
            stmt = self._base_query().where(User.username == username)
            return session.execute(stmt).scalar_one_or_none()

    # =========================
    # SAVE
    # =========================

    def save(self, user: User) -> User:
        with self.session_factory() as session:
            # merge — КЛЮЧЕВОЙ МОМЕНТ
            # работает и для новых, и для существующих объектов
            db_user = session.merge(user)

            session.commit()

            # важно: прогружаем связи ДО закрытия сессии
            session.refresh(db_user)

            return db_user

    # =========================
    # ALL
    # =========================

    def all(self) -> list[User]:
        with self.session_factory() as session:
            stmt = self._base_query()
            return list(session.execute(stmt).scalars().all())

    # =========================
    # DELETE
    # =========================

    def delete(self, user_id: int) -> None:
        with self.session_factory() as session:
            user = session.get(User, user_id)

            if user:
                session.delete(user)
                session.commit()

    # =========================
    # DELETE LIST
    # =========================

    def delete_list(self, user_id: int, list_id: int) -> bool:
        with self.session_factory() as session:
            stmt = (
                select(User)
                .options(
                    selectinload(User.listoftasks)
                )
                .where(User.id == user_id)
            )

            user = session.execute(stmt).scalar_one_or_none()
            if not user:
                return False

            for lst in user.listoftasks:
                if lst.id == list_id:
                    session.delete(lst)  # 🔥 ВАЖНО: удаляем через session
                    session.commit()
                    return True

            return False


    # =========================
    # DELETE TASK
    # =========================

    def delete_task(self, user_id: int, task_id: int) -> bool:
        with self.session_factory() as session:
            stmt = (
                select(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
                .where(User.id == user_id)
            )

            user = session.execute(stmt).scalar_one_or_none()
            if not user:
                return False

            for task_list in user.listoftasks:
                for task in task_list.tasks:
                    if task.id == task_id:
                        session.delete(task)  # 🔥 удаляем через ORM
                        session.commit()
                        return True

            return False


    # =========================
    # RESET ALL TASKS (simple)
    # =========================

    def reset_all_tasks_test(self) -> None:
        with self.session_factory() as session:
            stmt = (
                select(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
            )

            users = session.execute(stmt).scalars().all()

            for user in users:
                for task_list in user.listoftasks:
                    for task in task_list.tasks:
                        task.completed = False

            session.commit()

            print("Все задачи сброшены")


    # =========================
    # RESET ALL TASKS (с логикой poll)
    # =========================

    def reset_all_tasks(self) -> dict[int, list[dict]]:
        with self.session_factory() as session:
            stmt = (
                select(User)
                .options(
                    selectinload(User.listoftasks)
                    .selectinload(ListOfTasks.tasks)
                )
            )

            users = session.execute(stmt).scalars().all()

            result: dict[int, list[dict]] = {}

            for user in users:
                user_rows = []

                for task_list in user.listoftasks:

                    if not (task_list.active_poll_id and task_list.poll_voted):
                        continue

                    for task in task_list.tasks:
                        user_rows.append({
                            "username": user.username,
                            "list_title": task_list.title,
                            "task": task.value,
                            "completed": task.completed
                        })

                        # сброс задачи
                        task.completed = False

                    # сброс poll
                    task_list.poll_voted = False
                    task_list.active_poll_id = None
                    task_list.active_poll_message_id = None
                    task_list.active_poll_task_ids.clear()

                if user_rows:
                    result[user.id] = user_rows

            session.commit()

            return result