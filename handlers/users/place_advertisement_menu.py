from keyboards.inline.keyboards import ChatSelectionBuilder, VariousChatSelectionBuilder, PinTimeSelectionBuilder, InlineBuilder
from keyboards.inline.callbacks import ActionCallback
from forms.forms import PlaceAdvertisementForm
from data.config import MenuReferences, tools
from database.models import Chat, ChatGroup
from aiogram.fsm.context import FSMContext
from forms.forms import ElectiveChatGroup
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from states.states import StateGroup
from typing import Final, Dict, List
from data.texts import texts
from loader import postgres
from aiogram import Router
from aiogram import F


place_advertisement_menu_router: Final[Router] = Router(name='place_advertisement_menu')


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == ChatSelectionBuilder.get_menu_level()),
    StateFilter(StateGroup.place_advertisement)
)
async def handle_chat_selection(call: CallbackQuery, state: FSMContext):
    async def open_pin_time_selection_menu():
        pin_time_selection: PinTimeSelectionBuilder = PinTimeSelectionBuilder()
        menu_references.TO_PIN_TIME_SELECTION = call.data

        await call.message.edit_text(
            text=texts.get("select_pin_time"),
            reply_markup=pin_time_selection.get_keyboard(back_callback=menu_references.TO_CHAT_PICK)
        )

    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]

    place_advertisement_form: Final[PlaceAdvertisementForm] = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )
    menu_references: Final[MenuReferences] = await tools.deserializer.deserialize(encoded_menu_references)

    if callback_components.action == "select_various_chats":
        chats: Final[List[Chat]] = await postgres.get_chats()
        various_chat_selection: Final[VariousChatSelectionBuilder] = VariousChatSelectionBuilder(chats)

        await call.message.edit_text(
            text=texts.get("select_various_chats"),
            reply_markup=various_chat_selection.get_keyboard(menu_references.TO_CHAT_PICK)
        )

        encoded_various_chat_selection: str = await tools.serializer.serialize(various_chat_selection)
        menu_references.TO_VARIOUS_CHAT_PICK = call.data
        state_data["various_chat_selection"] = encoded_various_chat_selection
        state_data["pagination"] = encoded_various_chat_selection

    elif callback_components.action == "select_all":
        place_advertisement_form.chats = await postgres.get_chat_ids()
        await open_pin_time_selection_menu()

    elif callback_components.action.isnumeric():
        selected_chat_group: Final[ChatGroup] = await postgres.get_chat_group(callback_components.action)
        place_advertisement_form.chats = selected_chat_group
        await open_pin_time_selection_menu()

    encoded_menu_references: str = await tools.serializer.serialize(menu_references)
    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    state_data["menu_references"] = encoded_menu_references

    await state.set_data(state_data)


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == VariousChatSelectionBuilder.get_menu_level()),
    StateFilter(StateGroup.place_advertisement)
)
async def handle_various_chat_selection(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_place_advertisement_form: bytes = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]
    encoded_various_chat_selection: str = state_data["pagination"]

    various_chat_selection: VariousChatSelectionBuilder = await tools.deserializer.deserialize(
        encoded_various_chat_selection
    )
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )
    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)

    if callback_components.action == "submit":
        if len(various_chat_selection.selected_chats) == 0:
            await call.answer(
                show_alert=True,
                text="Нужно выбрать хотя бы один чат"
            )

        else:
            elective_chat_group: ElectiveChatGroup = ElectiveChatGroup()
            elective_chat_group.chats = various_chat_selection.selected_chats.copy()
            place_advertisement_form.chats = elective_chat_group
            pin_time_selection: PinTimeSelectionBuilder = PinTimeSelectionBuilder()
            menu_references.TO_PIN_TIME_SELECTION = call.data
            await call.message.edit_text(
                text=texts.get("select_pin_time"),
                reply_markup=pin_time_selection.get_keyboard(back_callback=menu_references.TO_VARIOUS_CHAT_PICK)
            )

    elif callback_components.action == "all_chats":
        chat_ids: List[int] = await postgres.get_chat_ids()

        if len(chat_ids) == len(various_chat_selection.selected_chats):
            various_chat_selection.unmark_all_as_selected()

        else:
            various_chat_selection.mark_all_as_selected(chat_ids)

        await call.message.edit_reply_markup(
            reply_markup=various_chat_selection.get_keyboard(menu_references.TO_CHAT_PICK)
        )

    elif callback_components.action.isnumeric():
        chat_id: str = callback_components.action
        if chat_id not in various_chat_selection.selected_chats:
            various_chat_selection.mark_as_selected(chat_id)

        else:
            various_chat_selection.unmark_as_selected(chat_id)

        await call.message.edit_reply_markup(
            reply_markup=various_chat_selection.get_keyboard(menu_references.TO_CHAT_PICK)
        )

    encoded_menu_references: str = await tools.serializer.serialize(menu_references)
    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    encoded_various_chat_selection: str = await tools.serializer.serialize(various_chat_selection)
    state_data["various_chat_selection"] = encoded_various_chat_selection
    state_data["pagination"] = encoded_various_chat_selection
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    state_data["menu_references"] = encoded_menu_references
    await state.set_data(state_data)


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == PinTimeSelectionBuilder.get_menu_level()),
    StateFilter(StateGroup.place_advertisement)
)
async def handle_pin_time_selection(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]

    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    if callback_components.action == "no_pin":
        place_advertisement_form.pin_days = 0
        await call.answer(f"Вы выбрали размещение без закрепления ✅")

    elif callback_components.action == "write_days_count":
        await call.message.edit_text(
            text=texts.get("enter_number_of_pin_days"),
            reply_markup=InlineBuilder().get_back_button_keyboard(
                back_callback=menu_references.TO_PIN_TIME_SELECTION
            )
        )

    elif callback_components.action.isnumeric():
        pin_days: Final[int] = int(callback_components.action)
        place_advertisement_form.pin_days = pin_days
        await call.answer(f"Вы выбрали закреп на {pin_days} дня / дней ✅")

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)


