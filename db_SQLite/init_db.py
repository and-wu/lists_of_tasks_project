from db_SQLite.db import Base, engine
from domain.SQLite_models import users, tasks, tasks_list

def init_db():

    print("Tables BEFORE:", Base.metadata.tables)

    # создаем в безе все таблицы которых еще нет,
    # не наполняем данными, а именно создаём структуру таблиц
    Base.metadata.create_all(bind=engine)

    print("Tables AFTER:", Base.metadata.tables)

print("DB initialized")
