from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# указываю путь сохранения базы
DATABASE_URL = f"sqlite:///app.db"

# создаю объект engine который знает как и к какой базе подключаться
engine = create_engine(DATABASE_URL, echo=False)

# создаем фабрику для создания сессий (session)
SessionLocal = sessionmaker(bind=engine,
                            autoflush=False,
                            autocommit=False,
                            expire_on_commit=False
                            )

# создаем базовый класс для всех моделей SQLAlchemy,
# используем его что бы понять какие есть модели и какие таблицы нужно создать
class Base(DeclarativeBase):
    pass
