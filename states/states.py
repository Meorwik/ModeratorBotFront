from aiogram.fsm.state import StatesGroup, State


class StateGroup(StatesGroup):
    place_advertisement: State = State()
    write_pin_days_count: State = State()

