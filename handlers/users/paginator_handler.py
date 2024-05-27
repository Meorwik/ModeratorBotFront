from keyboards.inline.callbacks import PaginationCallback
from keyboards.inline.base import PageableKeyboard
from forms.enums import PaginationActionTypes
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from data.config import tools
from aiogram import Router
from typing import Final


paginator_router: Final[Router] = Router(name='paginator')


@paginator_router.callback_query(PaginationCallback.filter())
async def handle_menu_pagination(call: CallbackQuery, state: FSMContext):
    callback_components = PaginationCallback.unpack(call.data)
    state_data = await state.get_data()

    encoded_paginator: str = state_data["pagination"]
    paginator: PageableKeyboard = await tools.deserializer.deserialize(encoded_paginator)

    if callback_components.action == PaginationActionTypes.open_next_page:
        paginator.open_next_page()

    elif callback_components.action == PaginationActionTypes.open_previous_page:
        paginator.open_previous_page()

    else:
        await call.answer(text="123", show_alert=True)

    await call.message.edit_reply_markup(reply_markup=paginator.get_keyboard(paginator.back_callback))
    encoded_paginator: str = await tools.serializer.serialize(paginator)
    state_data["pagination"] = encoded_paginator
    await state.set_data(state_data)
