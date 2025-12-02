from domain.task_list import ListOfTasks
from domain.tasks import Task
from domain.users import User
from infra.database import Database


db_path = "db.json"

db = Database(db_path)


print(db.read(use_mapping=False))
data = db.read()
print(data)

print(data[0].listoftasks[0].tasks[1].value)
print(data[0].listoftasks[0].add_task_to_list(Task(id=99, value="big task")))

db.save(data)





exit()

#name = input("введите ваше имя - ")

for user in data['users'][:1]:

    while True:
        task_name = input("напишите задачу - ")

        task1 = Task(id=10, value=task_name)

        task_lisl_1.add_task_to_list(task1)

        print(task_lisl_1.tasks)

        user.listoftasks.append(task_lisl_1)



