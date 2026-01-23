from aiogram.fsm.state import StatesGroup, State


class SheetStates(StatesGroup):
    waiting_for_google_sheet_link = State()
