from keyboards.inline.keyboards import ChatGroupSelectionBuilder, \
    VariousChatSelectionBuilder, PinTimeSelectionBuilder, \
    InlineBuilder, PlacementTypeSelection, CompletePlaceAdvertisementFormMenu
from forms.enums import PlacementTypesMediaPaths, PlacementTypes, PlacementTypesDescription, \
    PlacementTypesNames, PlacementTypesRequirements, AllowedContentTypes
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, \
    InputMediaDocument, InputMediaAudio, InputMediaVideo, ReplyKeyboardRemove
from forms.forms import PlaceAdvertisementForm, ElectiveChatGroup, UserForm
from utils.validators import IntegerValidator, StringValidator, MediaValidator
from middlewares.album_middleware import AlbumMiddleware, AlbumMedia
from keyboards.inline.callbacks import ActionCallback, BackCallback
from database.models import Chat, ChatGroup, ModerationRequest
from data.config import MenuReferences, tools, meta, config
from keyboards.default.keyboards import WebAppKeyboard
from aiogram.exceptions import TelegramBadRequest
from utils.price_counter import PriceCounter
from typing import Final, Dict, List, Union
from aiogram.fsm.context import FSMContext
from data.texts import texts, templates
from aiogram.filters import StateFilter
from states.states import StateGroup
from loader import bot, postgres
from aiogram import Router, F
from redis import Redis


place_advertisement_menu_router: Final[Router] = Router(name='place_advertisement_menu')
write_message_to_place: Final[Router] = Router(name="write_message_to_place")
write_message_to_place.message.middleware(AlbumMiddleware())
place_advertisement_menu_router.include_router(write_message_to_place)

MEDIA_GROUP_TYPES = {
    "audio": InputMediaAudio,
    "document": InputMediaDocument,
    "photo": InputMediaPhoto,
    "video": InputMediaVideo,
}


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


async def get_message_text(message: Message, album: List[AlbumMedia] = None):
    text: str = ""

    if message.text is not None:
        text = message.text

    elif message.caption is not None:
        text = message.caption

    else:
        if album:
            for i in album:
                if i.caption is not None:
                    text = i.caption

    return text


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == ChatGroupSelectionBuilder.get_menu_level()),
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
        elective_chat_group: ElectiveChatGroup = ElectiveChatGroup()
        elective_chat_group.all_city = True
        elective_chat_group.chats = await postgres.get_chat_ids()
        place_advertisement_form.chats = elective_chat_group
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
            if len(await postgres.get_chat_ids()) == len(elective_chat_group.chats):
                elective_chat_group.all_city = True

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

    menu_references.TO_PLACEMENT_TYPE_SELECTION = call.data

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
            photo=FSInputFile(PlacementTypesMediaPaths.get_type(current_option).value),
            caption=empty_template.format(
                option=f"{placement_type_selection.option_number}",
                placement_type=PlacementTypesNames.get_type(placement_type_selection.option_number).value,
                description=PlacementTypesDescription.get_type(placement_type_selection.option_number).value,
                datetime=texts.get("datetime_default_string")
            ),
            reply_markup=placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

        current_menu_message_id = new_message.message_id

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    encoded_menu_references: str = await tools.serializer.serialize(menu_references)

    state_data["menu_references"] = encoded_menu_references
    state_data["current_menu_message_id"] = current_menu_message_id
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
            photo=FSInputFile(PlacementTypesMediaPaths.get_type(current_option).value),
            caption=empty_template.format(
                option=f"{placement_type_selection.option_number}",
                placement_type=PlacementTypesNames.get_type(placement_type_selection.option_number).value,
                description=PlacementTypesDescription.get_type(placement_type_selection.option_number).value,
            ),
            reply_markup=placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

        current_menu_message_id = new_message.message_id

    else:
        await message.answer("❌Количество дней не должно быть больше 31!")
        await message.delete()

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
    current_message_id: int = call.message.message_id

    if callback_components.action == "select_option":
        if not placement_type_selection.is_marked():
            placement_type_selection.mark_option()
            place_advertisement_form.placement_type = PlacementTypes.get_type(placement_type_selection.option_number)

        else:
            placement_type_selection.unmark_option()
            place_advertisement_form.placement_type = None

        await call.message.edit_reply_markup(
            reply_markup=placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

    elif "option" in callback_components.action:
        placement_type_selection.unmark_option()
        place_advertisement_form.placement_type = None

        if "next" in callback_components.action:
            placement_type_selection.next_option()

        elif "previous" in callback_components.action:
            placement_type_selection.previous_option()

        empty_template: str = templates.get("placement_type_selection")
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(PlacementTypesMediaPaths.get_type(placement_type_selection.option_number).value)
            )
        )

        await call.message.edit_caption(
            caption=empty_template.format(
                option=f"{placement_type_selection.option_number}",
                placement_type=PlacementTypesNames.get_type(placement_type_selection.option_number).value,
                description=PlacementTypesDescription.get_type(placement_type_selection.option_number).value,
                datetime=texts.get("datetime_default_string")
            ),
            reply_markup=placement_type_selection.get_keyboard(menu_references.TO_PIN_TIME_SELECTION)
        )

    elif callback_components.action == "send_message":
        if place_advertisement_form.placement_type is not None:
            menu_references.TO_WRITE_MESSAGE = call.data
            await call.message.delete()
            new_message = await call.message.answer(
                text=PlacementTypesRequirements.get_type(placement_type_selection.option_number).value,
                reply_markup=InlineBuilder().get_back_button_keyboard(menu_references.TO_PLACEMENT_TYPE_SELECTION)
            )
            current_message_id: int = new_message.message_id
            await state.set_state(StateGroup.write_message_to_place)

        else:
            await call.answer(show_alert=True, text="Вы не выбрали механику размещения")

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    encoded_menu_references: str = await tools.serializer.serialize(menu_references)
    encoded_placement_type_selection: str = await tools.serializer.serialize(placement_type_selection)

    state_data["menu_references"] = encoded_menu_references
    state_data["current_menu_message_id"] = current_message_id
    state_data["placement_type_selection"] = encoded_placement_type_selection
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)


@write_message_to_place.message(
    StateFilter(StateGroup.write_message_to_place),
)
async def handle_write_message_to_place(message: Message, state: FSMContext, album: List[AlbumMedia] = None):
    state_data: Dict = await state.get_data()

    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]

    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    media_validator: MediaValidator = MediaValidator()
    placement_type: PlacementTypes = place_advertisement_form.placement_type
    got_message: bool = True

    if placement_type == PlacementTypes.message_from_bot:
        place_advertisement_form.message.is_forward = False
        place_advertisement_form.message.album = []
        place_advertisement_form.message.is_document = False

        if album:
            max_text_length: int = 900
            place_advertisement_form.message.album = album

        elif media_validator.has_media(message):
            max_text_length: int = 900
            is_valid: bool = media_validator.validate(message)

            if is_valid:

                if message.photo:
                    place_advertisement_form.message.album.append(
                        AlbumMedia(photo=message.photo[-1].file_id, caption=message.caption)
                    )

                elif message.video:
                    place_advertisement_form.message.album.append(
                        AlbumMedia(video=message.video.file_id, caption=message.caption)
                    )

                elif message.document is not None:
                    place_advertisement_form.message.is_document = True
                    place_advertisement_form.message.document = message.document.file_id

            else:
                got_message: bool = False
                await message.answer(
                    """
                    Данный тип медиа не поддерживается ❌
                    """
                )
                await message.delete()

        else:
            max_text_length: int = 4000

        text: str = await get_message_text(message, album)

        if text is not None:
            str_validator: StringValidator = StringValidator(
                max_string_length=max_text_length
            )

            is_valid: bool = str_validator.validate(text)

            if is_valid:
                place_advertisement_form.message.text = text

            else:
                got_message: bool = False
                await message.answer(
                    """
                    Ваше сообщение слишком большое ❌\nПожалуйста убедитесь в том, 
                    что ваше сообщение соответствует требованиям выше.
                    """
                )

        has_media: bool = len(place_advertisement_form.message.album) != 0

    else:
        place_advertisement_form.message.is_forward = True
        if album:
            got_message: bool = False
            await message.answer(
                """
                Ваше сообщение имеет больше одного медиа-файла ❌\nПожалуйста убедитесь в том, 
                что ваше сообщение соответствует требованиям выше.
                """
            )
            await message.delete()

        else:
            place_advertisement_form.message.message_id = message.message_id
            place_advertisement_form.message.text = message.text
        has_media: bool = False

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)

    final_keyboard: CompletePlaceAdvertisementFormMenu = \
        CompletePlaceAdvertisementFormMenu(
            placement_type=placement_type,
            has_media=has_media,
            is_document=place_advertisement_form.message.is_document
        )

    if got_message:
        await message.answer(
            text=texts.get("check_post_details").format(text=place_advertisement_form.message.text),
            reply_markup=final_keyboard.get_keyboard(menu_references.TO_WRITE_MESSAGE)
        )

        await state.set_state(StateGroup.place_advertisement)

    else:
        return None


@place_advertisement_menu_router.message(
    F.text == texts.get("back_button"),
    StateFilter(StateGroup.write_datetime_web_data)
)
@place_advertisement_menu_router.callback_query(
    BackCallback.filter(F.go_to == "complete_keyboard"),
)
async def handle_back_from_attach_media(msg: Union[CallbackQuery, Message], state: FSMContext):
    state_data: Dict = await state.get_data()
    encoded_menu_references: str = state_data["menu_references"]
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]

    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    has_media: bool = len(place_advertisement_form.message.album) != 0

    final_keyboard: CompletePlaceAdvertisementFormMenu = \
        CompletePlaceAdvertisementFormMenu(
            placement_type=place_advertisement_form.placement_type,
            has_media=has_media,
            is_document=place_advertisement_form.message.is_document
        )

    if isinstance(msg, CallbackQuery):
        await msg.message.edit_text(
            text=texts.get("check_post_details").format(text=place_advertisement_form.message.text),
            reply_markup=final_keyboard.get_keyboard(menu_references.TO_WRITE_MESSAGE)
        )

    else:
        await msg.delete()
        message_to_delete = await msg.answer(
            text="Загрузка...",
            reply_markup=ReplyKeyboardRemove()
        )
        await message_to_delete.delete()
        await msg.answer(
            text=texts.get("check_post_details").format(text=place_advertisement_form.message.text),
            reply_markup=final_keyboard.get_keyboard(menu_references.TO_WRITE_MESSAGE)
        )

    await state.set_state(StateGroup.place_advertisement)


@write_message_to_place.message(StateFilter(StateGroup.write_attach_media))
async def handle_attach_media(message: Message, state: FSMContext, album: List[AlbumMedia] = None):
    state_data: Dict = await state.get_data()
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]

    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    str_validator: StringValidator = StringValidator()

    text: str = await get_message_text(message, album)
    got_message: bool = False

    is_valid = str_validator.validate(text)

    if is_valid:
        if album:
            place_advertisement_form.message.album += album
            got_message = True

        else:
            if message.content_type != AllowedContentTypes.video.value \
                    and message.content_type != AllowedContentTypes.photo.value:

                await message.answer("❌ Ошибка! \nФайл должен быть либо фото, либо видео")
                await message.delete()

            else:
                if message.photo:
                    place_advertisement_form.message.album.append(
                        AlbumMedia(photo=message.photo[-1].file_id, caption=message.caption)
                    )

                elif message.video:
                    place_advertisement_form.message.album.append(
                        AlbumMedia(video=message.video.file_id, caption=message.caption)
                    )

                got_message = True

        if place_advertisement_form.message.text is not None:
            place_advertisement_form.message.album[0].caption = place_advertisement_form.message.text

    else:
        await message.answer("❌ Ошибка!\nФайл должен быть отправлен без текста!")
        await message.delete()

    if got_message:
        await message.answer(
            text="Принято!✅\nВы можете продолжить, либо вернуться ",
            reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard"))
        )

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)


@place_advertisement_menu_router.callback_query(
    ActionCallback.filter(F.menu_level == CompletePlaceAdvertisementFormMenu.get_menu_level())
)
async def handle_complete_keyboard(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    encoded_menu_references: str = state_data["menu_references"]

    menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    if callback_components.action == "complete":
        if bool(place_advertisement_form.message.text) or \
                bool(place_advertisement_form.message.album):
            web_app_keyboard: WebAppKeyboard = WebAppKeyboard()
            await call.message.delete()
            await call.message.answer(
               text=texts.get("choose_publish_datetime"),
               reply_markup=web_app_keyboard.get_keyboard()
            )
            await state.set_state(StateGroup.write_datetime_web_data)

        else:
            await call.answer("❌ Ошибка!\nВаше сообщение пустое!")

    elif callback_components.action == "modify":
        if place_advertisement_form.placement_type == PlacementTypes.message_from_bot:
            await call.message.edit_text(
                reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard")),
                text=texts.get("message_from_bot_requirements")
            )
            await state.set_state(StateGroup.write_message_to_place)

    elif callback_components.action == "attach_media":
        await call.message.edit_text(
            text=texts.get("attach_media_text"),
            reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard"))
        )
        await state.set_state(StateGroup.write_attach_media)

    elif callback_components.action == "delete_all_media":
        place_advertisement_form.message.album = []
        place_advertisement_form.message.document = None
        await call.answer(show_alert=True, text="Все медиа файлы успешно удалены!")
        await call.message.edit_reply_markup(
            reply_markup=CompletePlaceAdvertisementFormMenu(
                place_advertisement_form.placement_type, has_media=False
            ).get_keyboard(menu_references.TO_WRITE_MESSAGE)
        )

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    encoded_menu_references: str = await tools.serializer.serialize(menu_references)

    state_data["menu_references"] = encoded_menu_references
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)


@place_advertisement_menu_router.message(
    F.web_app_data,
    StateFilter(StateGroup.write_datetime_web_data)
)
async def handle_datetime_choice(message: Message, state: FSMContext):
    state_data: Dict = await state.get_data()
    encoded_place_advertisement_form: str = state_data["place_advertisement_form"]
    place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
        encoded_place_advertisement_form
    )

    datetime_separator: Final[str] = ";"
    date, time = message.web_app_data.data.split(datetime_separator)

    place_advertisement_form.date = date
    place_advertisement_form.time = time

    price_counter: Final[PriceCounter] = PriceCounter(place_advertisement_form)
    place_advertisement_form.total_cost = await price_counter.count_price()
    from_user: Final[UserForm] = UserForm(
        id=message.from_user.id,
        username=message.from_user.username
    )
    place_advertisement_form.message.from_user = from_user

    encoded_place_advertisement_form: str = await tools.serializer.serialize(place_advertisement_form)
    state_data["place_advertisement_form"] = encoded_place_advertisement_form
    await state.set_data(state_data)

    moderation_request: ModerationRequest = ModerationRequest(
        from_user=from_user.id,
        form=encoded_place_advertisement_form
    )
    await postgres.add_moderation_request(moderation_request)

    redis: Redis = Redis.from_url(url=config.REDIS_URL)
    admin_id = redis.get("admin")
    redis.close()

    message_to_delete: Message = await message.answer(
        text="Загрузка...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message_to_delete.delete()

    await message.answer(
        text=templates.get("complete_place_advertisement").format(price=place_advertisement_form.total_cost),
        reply_markup=InlineBuilder().get_back_button_keyboard()
    )

    await bot.send_message(
        chat_id=admin_id,
        text="<b>У вас новый запрос на модерацию!</b>",
    )

