from aiogram.fsm.state import StatesGroup, State

class ListStates(StatesGroup):
    waiting_for_list_name = State()
    waiting_for_remind_decision = State()
    waiting_for_remind_time = State()
    waiting_for_edit_remind_time = State()
    waiting_for_notification_type = State()
    waiting_for_repeat_type = State()
    waiting_for_run_date = State()
