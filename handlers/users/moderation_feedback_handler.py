from keyboards.inline.admin_keyboards import DeclinedPostKeyboard, InlineBuilder
from forms.enums import PlacementTypesRequirements, PlacementTypes
from keyboards.inline.callbacks import ActionCallback
from forms.forms import PlaceAdvertisementForm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from .main_menu import reopen_main_menu
from data.config import MenuReferences
from states.states import StateGroup
from typing import Final, Dict
from data.config import tools
from aiogram import Router, F


moderation_feedback_router: Final[Router] = Router(name="moderation_feedback")


@moderation_feedback_router.callback_query(ActionCallback.filter(F.menu_level == DeclinedPostKeyboard.get_menu_level()))
async def handel_moderation_feedback(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]

    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    if "edit_post" in callback_components.action:
        if place_advertisement_form.placement_type == PlacementTypes.message_from_bot:
            option_number: int = 1

        elif place_advertisement_form.placement_type == PlacementTypes.group_repost:
            option_number: int = 2

        elif place_advertisement_form.placement_type == PlacementTypes.direct_messages_repost:
            option_number: int = 3

        else:
            option_number: int = 0

        menu_references.TO_WRITE_MESSAGE = call.data
        await call.message.delete()
        await call.message.answer(
            text=PlacementTypesRequirements.get_type(option_number).value,
            reply_markup=InlineBuilder().get_back_button_keyboard(menu_references.TO_PLACEMENT_TYPE_SELECTION)
        )
        await state.set_state(StateGroup.write_message_to_place)

    elif callback_components.action == "cancel_post":
        await reopen_main_menu(call)

    await state.set_data(state_data)
