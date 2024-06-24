from keyboards.inline.admin_keyboards import AdminMainMenuKeyboard, AdminModerationKeyboard, DeclinedPostKeyboard, \
    InlineBuilder, ContinueModerationKeyboard

from keyboards.inline.callbacks import AdminCallback, BackCallback
from database.models import ModerationRequest, ModerationStatus
from utils.advertisement_sender import AdvertisementSender
from aiogram.types import CallbackQuery, Message
from forms.forms import PlaceAdvertisementForm
from filters.admin_filter import AdminFilter
from data.config import AdminMenuReferences
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from data.texts import texts, templates
from states.states import StateGroup
from typing import Final, List, Dict
from data.config import tools
from loader import postgres
from aiogram import Router
from loader import bot
from aiogram import F


admin_router: Final[Router] = Router(name="admin")
admin_filter: Final[AdminFilter] = AdminFilter()


async def send_next_post_on_moderation(state_data: Dict, call: CallbackQuery, state: FSMContext):
    advertisement_sender: Final[AdvertisementSender] = AdvertisementSender()
    moderation_request: Final[ModerationRequest] = await postgres.get_moderation_request()

    if moderation_request is not None:
        state_data["current_moderation_request"] = await tools.serializer.serialize(moderation_request)

        await advertisement_sender.send_to_admin_on_moderation(
            place_advertisement_form=moderation_request.form,
            admin_id=call.from_user.id
        )

        await call.message.delete()
        await state.set_state(StateGroup.admin_in_moderation)

    else:
        await call.answer("❌Сейчас нет заявок на модерацию!")


@admin_router.callback_query(
    BackCallback.filter(F.go_to == "AdminMainMenu")
)
async def open_main_menu(call: CallbackQuery, state: FSMContext):
    admin_keyboard: Final[AdminMainMenuKeyboard] = AdminMainMenuKeyboard()

    await call.message.edit_text(
        text=templates.get("admin_greeting").format(
            admin_username=call.message.from_user.username,
            new_users=await postgres.count_users_joined_today(),
            posts_waiting_count=await postgres.count_requests_waiting_for_moderation(),
        ),
        reply_markup=admin_keyboard.get_keyboard()
    )
    await state.set_state(StateGroup.admin)


@admin_router.callback_query(
    AdminCallback.filter(F.menu_level == AdminMainMenuKeyboard.get_menu_level()),
)
async def handle_main_admin_menu(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    admin_menu_references: AdminMenuReferences = AdminMenuReferences()
    state_data: Dict = await state.get_data()

    if callback_components.action == "statistics":
        ...

    elif callback_components.action == "placements":
        ...

    elif callback_components.action == "start_moderation":
        admin_menu_references.TO_POST_MODERATION = call.data
        await send_next_post_on_moderation(
            state_data=state_data,
            state=state,
            call=call
        )

    encoded_admin_menu_references: str = await tools.serializer.serialize(admin_menu_references)
    state_data["admin_menu_references"] = encoded_admin_menu_references
    await state.set_data(state_data)


@admin_router.callback_query(
    AdminCallback.filter(F.menu_level == AdminModerationKeyboard.get_menu_level()),
)
async def handle_post_moderation(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_admin_menu_references: str = state_data["admin_menu_references"]
    encoded_current_moderation_request: str = state_data["current_moderation_request"]

    current_moderation_request: ModerationRequest = await tools.deserializer.deserialize(
        encoded_current_moderation_request
    )
    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)

    if callback_components.action == "approved":
        await postgres.change_moderation_request_status(
            moderation_request_id=current_moderation_request.id,
            status=ModerationStatus.approved
        )
        await call.message.edit_text(
            text="Пост успешно прошел модерацию!✅",
            reply_markup=ContinueModerationKeyboard().get_keyboard()
        )

    elif callback_components.action == "make_notes":
        await call.message.edit_text(
            text="Напишите, что нужно изменить",
            reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_POST_MODERATION)
        )
        await state.set_state(StateGroup.admin_writing_notes)


@admin_router.message(
    StateFilter(StateGroup.admin_writing_notes)
)
async def handle_writing_notes(message: Message, state: FSMContext):
    if message.text:
        state_data: Dict = await state.get_data()
        encoded_current_moderation_request: str = state_data["current_moderation_request"]
        current_moderation_request: ModerationRequest = await tools.deserializer.deserialize(
            encoded_current_moderation_request
        )

        notes: Final[str] = message.text

        await message.answer(
            text="Ваши рекомендации отправлены пользователю.",
            reply_markup=ContinueModerationKeyboard().get_keyboard()
        )

        await postgres.change_moderation_request_status(
            moderation_request_id=current_moderation_request.id,
            status=ModerationStatus.declined
        )

        place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
            current_moderation_request.form
        )
        await bot.send_message(
            chat_id=place_advertisement_form.message.from_user.id,
            text=templates.get("post_declined").format(notes=notes),
            reply_markup=DeclinedPostKeyboard().get_keyboard()
        )
        await state.set_state(StateGroup.admin_in_moderation)

    else:
        await message.answer("Ошибка!\nСообщение должно содержать только текст ")


@admin_router.callback_query(
    AdminCallback.filter(F.menu_level == ContinueModerationKeyboard.get_menu_level())
)
async def handle_continue_moderation(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    if callback_components.action == "continue":
        await send_next_post_on_moderation(
            state_data=state_data,
            state=state,
            call=call
        )

    await state.set_data(state_data)

