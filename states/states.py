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

    in_payment_stage: State = State()
    write_payment_check: State = State()
    write_datetime_web_data_payment_stage: State = State()

    in_post_settings: State = State()
    in_post_modify: State = State()
    admin_write_attach_media: State = State()
    admin_write_pin_days_count: State = State()


