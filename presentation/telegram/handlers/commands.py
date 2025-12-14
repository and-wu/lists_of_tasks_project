from pathlib import Path

from aiogram import types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from application.user.create_user import UserService
from presentation.telegram.custom_router import ControllerRouter
from presentation.telegram.states import SelectTaskList
from presentation.telegram.texts import main_menu, say_hello, successful_list_create_text, show_lists_of_tasks, \
    not_lists_user, not_tasks_text, show_tasks, get_list_id, successful_choice_list, successful_task_create

commands_router = ControllerRouter()


# ==============================
#            /start
# ==============================
@commands_router.message(CommandStart())
async def cmd_start(message: Message, service: UserService):
    try:
        service.create_user(user_id=message.from_user.id, name=message.from_user.first_name,
                            username=message.from_user.username)
    except Exception as e:
        print(e)

    await message.answer(say_hello(username=message.from_user.first_name))

    await message.answer(main_menu())


@commands_router.message(Command("create_list_of_tasks"))
async def cmd_create_list_of_tasks(message: Message, service: UserService):
    listoftask = service.add_list_of_tasks(message.from_user.id, message.text.split()[1])
    await message.answer(successful_list_create_text(list_of_tasks=listoftask))


@commands_router.message(Command("show_lists_of_tasks"))
async def cmd_show_lists_of_tasks(message: Message, service: UserService):
    user = service.get_user_by_id(message.from_user.id)

    if not user.listoftasks:
        await message.answer(not_lists_user())

    await message.answer(show_lists_of_tasks(user.listoftasks))


@commands_router.message(Command("show_tasks"))
async def cmd_show_tasks(message: Message, service: UserService):

    tasks = service.get_tasks(
        user_id=message.from_user.id,
        list_of_tasks_id=int(message.text.split()[1])
    )

    if not tasks:
        await message.answer(not_tasks_text())
        return

    await message.answer(show_tasks(tasks))



@commands_router.message(Command("create_task"))
async def cmd_create_task(message: Message, service: UserService, state: FSMContext):
    task = service.add_task(
        user_id=message.from_user.id,
        list_id=int(message.text.split()[1]),
        value=message.text.split()[2]
    )

    await message.answer(successful_task_create(task))

