from keyboards.inline.admin_keyboards import AdminMainMenuKeyboard, AdminModerationKeyboard, DeclinedPostKeyboard, \
    InlineBuilder, ContinueModerationKeyboard, StatisticsKeyboard, AcceptPaymentKeyboard
from keyboards.inline.keyboards import SelectPaymentMethodKeyboard, PaymentCheckResultKeyboard
from keyboards.inline.callbacks import AdminCallback, BackCallback, DataPassCallback
from database.models import ModerationRequest, ModerationStatus
from utils.advertisement_sender import AdvertisementSender
from forms.forms import ModeratedAdvertisementForm
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from forms.forms import PlaceAdvertisementForm
from data.config import AdminMenuReferences
from aiogram.fsm.context import FSMContext
from forms.forms import ElectiveChatGroup
from aiogram.filters import StateFilter
from data.texts import texts, templates
from states.states import StateGroup
from typing import Final, Dict
from data.config import tools
from loader import postgres
from aiogram import Router
from loader import bot
from aiogram import F


admin_router: Final[Router] = Router(name="admin")


async def get_main_admin_menu_text(call: CallbackQuery):
    text = templates.get("admin_greeting").format(
        admin_username=call.message.from_user.username,
        new_users=await postgres.count_users_joined_today(),
        posts_waiting_count=await postgres.count_requests_waiting_for_moderation(),
    )
    return text


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
        text=await get_main_admin_menu_text(call),
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
        admin_menu_references.TO_STATISTICS_MENU = call.data
        statistics_keyboard: Final[StatisticsKeyboard] = StatisticsKeyboard()
        await call.message.edit_text(
            text=await get_main_admin_menu_text(call),
            reply_markup=statistics_keyboard.get_keyboard(BackCallback(go_to="AdminMainMenu").pack())
        )

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

        encoded_place_advertisement_form: str = current_moderation_request.form
        place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
            encoded_place_advertisement_form
        )

        await bot.send_message(
            chat_id=place_advertisement_form.message.from_user.id,
            text=templates.get("approved_post_text").format(total_cost=place_advertisement_form.total_cost),
            reply_markup=SelectPaymentMethodKeyboard(current_moderation_request.id).get_keyboard()
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


@admin_router.callback_query(AdminCallback.filter(F.menu_level == StatisticsKeyboard.get_menu_level()))
async def handle_statistics_menu(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_admin_menu_references: str = state_data["admin_menu_references"]
    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)

    if callback_components.action == "income":
        await call.message.edit_text(
            text=templates.get("income_statistics").format(
                total_income=await postgres.count_total_income(),
                month_income=await postgres.count_month_income(),
                week_income=await postgres.count_week_income(),
                day_income=await postgres.count_day_income()
            ),
            reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_STATISTICS_MENU)
        )

    elif callback_components.action == "posts":
        await call.message.edit_text(
            text=templates.get("posts_statistics").format(
                all_posts_count=await postgres.count_all_posts(),
                placed_posts_count=await postgres.count_placed_posts(),
                placed_with_pin_count=await postgres.count_placed_with_pin(),
                placed_without_pin_count=await postgres.count_placed_without_pin(),
                posts_waiting_count=await postgres.count_requests_waiting_for_moderation()
            ),
            reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_STATISTICS_MENU)
        )

    elif callback_components.action == "users":
        await call.message.edit_text(
            text=templates.get("users_statistics").format(
                all_users_count=await postgres.count_all_users(),
                month_users=await postgres.count_users_joined_this_month(),
                week_users=await postgres.count_users_joined_this_week(),
                day_users=await postgres.count_users_joined_today()
            ),
            reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_STATISTICS_MENU)
        )


@admin_router.callback_query(DataPassCallback.filter(F.menu_level == AcceptPaymentKeyboard.get_menu_level()))
async def handle_payment_delivery(call: CallbackQuery, state: FSMContext):
    callback_components: DataPassCallback = DataPassCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    current_moderation_request_id: int = int(callback_components.data)
    current_moderation_request: ModerationRequest = await postgres.get_moderation_request_by_id(
        current_moderation_request_id
    )
    moderated_advertisement_form: ModeratedAdvertisementForm = ModeratedAdvertisementForm(
        request_id=current_moderation_request.id,
        advertisement_form=await tools.deserializer.deserialize(current_moderation_request.form)
    )

    if callback_components.action == "successful_payment":
        if isinstance(moderated_advertisement_form.advertisement_form.chats, ElectiveChatGroup):
            if moderated_advertisement_form.advertisement_form.chats.all_city:
                chat_name: str = "Весь город"
            else:
                chat_name: str = str(
                    moderated_advertisement_form.advertisement_form.chats.chats
                ).replace("[", "").replace("]", "")

        else:
            chat_name: str = moderated_advertisement_form.advertisement_form.chats.name

        await bot.send_message(
            chat_id=moderated_advertisement_form.advertisement_form.message.from_user.id,
            text=templates.get("successful_payment").format(
                text_part=moderated_advertisement_form.advertisement_form.message.text[:30],
                chats=chat_name,
                date=moderated_advertisement_form.advertisement_form.date,
                time=moderated_advertisement_form.advertisement_form.time
            ),
            reply_markup=PaymentCheckResultKeyboard(is_paid=True).get_keyboard()
        )
        username: str = moderated_advertisement_form.advertisement_form.message.from_user.username
        await call.answer(
            text=f"✅ Вы приняли подтверждение оплаты пользователя @{username}!",
            show_alert=True
        )
        await call.message.delete()

    elif callback_components.action == "failed_payment":
        await bot.send_message(
            chat_id=moderated_advertisement_form.advertisement_form.message.from_user.id,
            text=texts.get("failed_payment"),
            reply_markup=PaymentCheckResultKeyboard(is_paid=False).get_keyboard()
        )
        username: str = moderated_advertisement_form.advertisement_form.message.from_user.username
        await call.answer(
            text=f"❌ Вы отклонили подтверждение оплаты пользователя @{username}!",
            show_alert=True
        )
        await call.message.delete()

    try:
        await bot.delete_message(
            chat_id=call.from_user.id,
            message_id=call.message.message_id-1
        )

    except TelegramBadRequest:
        pass

    await state.set_data(state_data)
