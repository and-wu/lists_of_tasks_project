from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_SQLite.db import Base
from domain.task_list import ListOfTasks


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    google_sheet_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    # связь с ListOfTasks (TaskList)
    listoftasks: Mapped[list["ListOfTasks"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def rename(self, new_name: str):
        if len(new_name) < 2:
            raise ValueError("Name is too short")
        self.name = new_name