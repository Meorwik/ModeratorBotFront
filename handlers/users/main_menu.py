from keyboards.inline.keyboards import MainMenuBuilder, InlineBuilder, ChatSelectionBuilder
from keyboards.inline.callbacks import ActionCallback, BackCallback
from aiogram.types import InlineKeyboardMarkup
from forms.forms import PlaceAdvertisementForm
from data.config import MenuReferences, tools
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from states.states import StateGroup
from typing import Final, List, Dict
from database.models import ChatGroup
from data.texts import texts
from loader import postgres
from aiogram import Router
from aiogram import F


main_menu_router: Final[Router] = Router(name='main_menu')


async def reopen_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        text=texts.get("greetings"),
        reply_markup=MainMenuBuilder().get_keyboard()
    )


@main_menu_router.callback_query(ActionCallback.filter(F.menu_level == MainMenuBuilder.get_menu_level()))
async def handle_main_menu(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)

    if callback_components.action == "place_advertisement":
        chat_groups: List[ChatGroup] = await postgres.get_chat_groups()
        chat_selection_keyboard: ChatSelectionBuilder = ChatSelectionBuilder(chat_groups)
        await call.message.edit_text(
            text=texts.get("place_advertisement"),
            reply_markup=chat_selection_keyboard.get_keyboard()
        )

        await state.clear()
        await state.set_state(StateGroup.place_advertisement)
        state_data: Dict = await state.get_data()

        place_advertisement_form: Final[PlaceAdvertisementForm] = PlaceAdvertisementForm()
        menu_references: Final[MenuReferences] = MenuReferences()
        menu_references.TO_CHAT_PICK = call.data
        encoded_menu_references: str = await tools.serializer.serialize(menu_references)
        encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)

        state_data["place_advertisement_form"] = encoded_place_advertisement_form
        state_data["menu_references"] = encoded_menu_references
        await state.set_data(state_data)

    elif callback_components.action == "services_price":
        services_price_button_index: Final[int] = 1
        old_keyboard: List = call.message.reply_markup.inline_keyboard
        new_keyboard: List = old_keyboard.copy()
        new_keyboard.remove(old_keyboard[services_price_button_index])
        new_keyboard.append([InlineBuilder().get_back_button()])

        await call.message.edit_text(
            text=texts.get("services_price"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
        )
        

@main_menu_router.callback_query(BackCallback.filter(F.go_to == MainMenuBuilder.get_menu_level()))
async def handle_back_button(call: CallbackQuery):
    await reopen_main_menu(call)
