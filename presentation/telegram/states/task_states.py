from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    waiting_for_task_text = State()
    waiting_for_new_task_text = State()

