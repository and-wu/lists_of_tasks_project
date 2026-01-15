from aiogram.fsm.state import StatesGroup, State

class ListStates(StatesGroup):
    waiting_for_list_name = State()
    waiting_for_remind_decision = State()
    waiting_for_remind_time = State()
