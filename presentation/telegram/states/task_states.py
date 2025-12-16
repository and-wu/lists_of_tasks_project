from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    waiting_for_task_text = State()
