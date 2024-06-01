from keyboards.inline.keyboards import ChatSelectionBuilder, \
    VariousChatSelectionBuilder, PinTimeSelectionBuilder, \
    InlineBuilder, PlacementTypeSelection
from forms.forms import PlaceAdvertisementForm, ElectiveChatGroup
from forms.enums import PlacementTypesMediaPaths, PlacementTypes
from aiogram.types import CallbackQuery, Message, FSInputFile
from utils.validators.int_validator import IntegerValidator
from keyboards.inline.callbacks import ActionCallback
from data.config import MenuReferences, tools, meta
from aiogram.exceptions import TelegramBadRequest
from database.models import Chat, ChatGroup
from aiogram.fsm.context import FSMContext
from data.texts import texts, templates
from aiogram.filters import StateFilter
from states.states import StateGroup
from typing import Final, Dict, List
from loader import bot, postgres
from aiogram import Router, F


place_advertisement_menu_router: Final[Router] = Router(name='place_advertisement_menu')


async def open_pin_time_selection_menu(message: Message, back_callback, state_data: Dict):
    pin_time_selection: PinTimeSelectionBuilder = PinTimeSelectionBuilder()

    try:
        await message.edit_text(
            text=texts.get("select_pin_time"),
            reply_markup=pin_time_selection.get_keyboard(back_callback=back_callback)
        )

    except TelegramBadRequest:
        await message.delete()
        new_message = await message.answer(
            text=texts.get("select_pin_time"),
            reply_markup=pin_time_selection.get_keyboard(back_callback=back_callback)
        )
        state_data["current_menu_message_id"] = new_message.message_id


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == ChatSelectionBuilder.get_menu_level()),
)
async def handle_chat_selection(call: CallbackQuery, state: FSMContext):
    async def open_pin_time_selection_menu_from_chat_selection():
        menu_references.TO_PIN_TIME_SELECTION = call.data
        await open_pin_time_selection_menu(call.message, menu_references.TO_CHAT_PICK, state_data)

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
        await open_pin_time_selection_menu_from_chat_selection()

    elif callback_components.action.isnumeric():
        selected_chat_group: Final[ChatGroup] = await postgres.get_chat_group(callback_components.action)
        place_advertisement_form.chats = selected_chat_group
        await open_pin_time_selection_menu_from_chat_selection()

    encoded_menu_references: str = await tools.serializer.serialize(menu_references)
    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    state_data["menu_references"] = encoded_menu_references
    state_data["current_menu_message_id"] = call.message.message_id

    await state.set_data(state_data)


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == VariousChatSelectionBuilder.get_menu_level()),
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
            menu_references.TO_PIN_TIME_SELECTION = call.data

            await open_pin_time_selection_menu(call.message, menu_references.TO_VARIOUS_CHAT_PICK, state_data)

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

    placement_type_selection: PlacementTypeSelection = PlacementTypeSelection()
    encoded_placement_type_selection: str = await tools.serializer.serialize(placement_type_selection)
    state_data["placement_type_selection"] = encoded_placement_type_selection
    current_menu_message_id: int = call.message.message_id

    if callback_components.action == "write_days_count":
        await call.message.edit_text(
            text=texts.get("enter_number_of_pin_days"),
            reply_markup=InlineBuilder().get_back_button_keyboard(
                back_callback=menu_references.TO_PIN_TIME_SELECTION
            )
        )
        await state.set_state(StateGroup.write_pin_days_count)

    elif callback_components.action.isnumeric():
        pin_days: Final[int] = int(callback_components.action)
        place_advertisement_form.pin_days = pin_days
        if pin_days == 0:
            await call.answer(f"Вы выбрали размещение без закрепления ✅")

        else:
            await call.answer(f"Вы выбрали закреп на {pin_days} дня / дней ✅")

        empty_template: str = templates.get("placement_type_selection")
        current_option: Final[int] = placement_type_selection.option_number

        await call.message.delete()

        new_message = await call.message.answer_photo(
            photo=FSInputFile(PlacementTypesMediaPaths.get_picture(current_option).value),
            caption=empty_template.format(
                option=f"{current_option}",
                placement_type="2",
                description="3",
                datetime="4"
            ),
            reply_markup=placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

        current_menu_message_id = new_message.message_id
    state_data["current_menu_message_id"] = current_menu_message_id
    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)


@place_advertisement_menu_router.message(
    StateFilter(StateGroup.write_pin_days_count)
)
async def handle_write_pin_days_count(message: Message, state: FSMContext):
    state_data: Dict = await state.get_data()

    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    current_menu_message_id: int = state_data["current_menu_message_id"]
    encoded_menu_references: str = state_data["menu_references"]
    encoded_placement_type_selection: str = state_data["placement_type_selection"]

    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
    placement_type_selection: PlacementTypeSelection = await tools.deserializer.deserialize(
        encoded_placement_type_selection
    )
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    int_validator: IntegerValidator = IntegerValidator(
        max_possible_value=meta.MAX_PIN_DAYS_POSSIBLE
    )

    is_valid, value = int_validator.validate(message.text)

    if is_valid:
        place_advertisement_form.pin_days = value
        empty_template: str = templates.get("placement_type_selection")
        current_option: Final[int] = placement_type_selection.option_number

        await bot.delete_message(
            chat_id=message.from_user.id,
            message_id=current_menu_message_id
        )

        new_message = await message.answer_photo(
            photo=FSInputFile(PlacementTypesMediaPaths.get_picture(current_option).value),
            caption=empty_template.format(
                option=f"{current_option}",
                placement_type="2",
                description="3",
                datetime="4"
            ),
            reply_markup=placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

        current_menu_message_id = new_message.message_id

    else:
        return value

    await message.delete()
    await state.set_state(StateGroup.place_advertisement)
    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    encoded_placement_type_selection: str = await tools.serializer.serialize(placement_type_selection)

    state_data["current_menu_message_id"] = current_menu_message_id
    state_data["placement_type_selection"] = encoded_placement_type_selection
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == PlacementTypeSelection.get_menu_level()),
)
async def handle_placement_type_selection(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]
    encoded_placement_type_selection: str = state_data["placement_type_selection"]

    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )
    placement_type_selection: PlacementTypeSelection = await tools.deserializer.deserialize(
        encoded_placement_type_selection
    )
    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)

    if callback_components.action == "select_option":
        place_advertisement_form.placement_type = PlacementTypes.get_type(placement_type_selection.option_number).value

        if not placement_type_selection.is_marked():
            placement_type_selection.mark_option()

        else:
            placement_type_selection.unmark_option()

        await call.message.edit_reply_markup(
            placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

    elif callback_components.action == "previous_option":
        ...

    elif callback_components.action == "next_option":
        ...

    elif callback_components.action == "send_message":
        await call.message.answer(place_advertisement_form)

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    encoded_placement_type_selection: str = await tools.serializer.serialize(placement_type_selection)

    state_data["current_menu_message_id"] = call.message.message_id
    state_data["placement_type_selection"] = encoded_placement_type_selection
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)
