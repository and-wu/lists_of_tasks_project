from pathlib import Path

from aiogram import types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from application.user.create_user import UserService
from presentation.telegram.custom_router import ControllerRouter
from presentation.telegram.keyboards import get_main_menu_keyboard
from presentation.telegram.texts import get_main_menu_text, say_hello, get_list_created_text, get_lists_text, \
    get_no_lists_text, get_no_tasks_text, get_tasks_text, get_task_created_text

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

    text = (
            say_hello(username=message.from_user.first_name)
            + "\n\n"
            + get_main_menu_text()
    )

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

# @commands_router.message(Command("create_list_of_tasks"))
# async def cmd_create_list_of_tasks(message: Message, service: UserService):
#     listoftask = service.add_list_of_tasks(message.from_user.id, message.text.split()[1])
#     await message.answer(get_list_created_text(list_of_tasks=listoftask))
#
#
# @commands_router.message(Command("show_lists_of_tasks"))
# async def cmd_show_lists_of_tasks(message: Message, service: UserService):
#     user = service.get_user_by_id(message.from_user.id)
#
#     if not user.listoftasks:
#         await message.answer(get_no_lists_text())
#
#     await message.answer(get_lists_text(user.listoftasks))
#
#
# @commands_router.message(Command("show_tasks"))
# async def cmd_show_tasks(message: Message, service: UserService):
#
#     tasks = service.get_tasks(
#         user_id=message.from_user.id,
#         list_of_tasks_id=int(message.text.split()[1])
#     )
#
#     if not tasks:
#         await message.answer(get_no_tasks_text())
#         return
#
#
#     await message.answer(get_tasks_text(tasks))
#
#
#
# @commands_router.message(Command("create_task"))
# async def cmd_create_task(message: Message, service: UserService, state: FSMContext):
#     task = service.add_task(
#         user_id=message.from_user.id,
#         list_id=int(message.text.split()[1]),
#         value=message.text.split()[2]
#     )
#
#     await message.answer(get_task_created_text(task))
#
