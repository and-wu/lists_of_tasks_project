from aiogram.fsm.state import State, StatesGroup


class ListStates(StatesGroup):
    waiting_for_list_name = State()
    waiting_for_remind_decision = State()
    waiting_for_remind_time = State()
