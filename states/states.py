from aiogram.fsm.state import StatesGroup, State


class StateGroup(StatesGroup):
    place_advertisement: State = State()
    write_pin_days_count: State = State()
    write_message_to_place: State = State()
    write_attach_media: State = State()
    write_datetime_web_data: State = State()

    admin: State = State()
    admin_in_moderation: State = State()
    admin_writing_notes: State = State()

