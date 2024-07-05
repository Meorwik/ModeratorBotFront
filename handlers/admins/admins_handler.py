from keyboards.inline.admin_keyboards import AdminMainMenuKeyboard, AdminModerationKeyboard, DeclinedPostKeyboard, \
    InlineBuilder, ContinueModerationKeyboard, StatisticsKeyboard, AcceptPaymentKeyboard, CalendarKeyboard, \
    PostSelectionKeyboard, PostInteractionKeyboard, PostCancellationConfirmKeyboard, PostModifyKeyboard, \
    AdminPinTimeSelectionBuilder
from keyboards.inline.keyboards import SelectPaymentMethodKeyboard, PaymentCheckResultKeyboard
from keyboards.inline.callbacks import AdminCallback, BackCallback, DataPassCallback
from forms.forms import ModeratedAdvertisementForm, PlaceAdvertisementForm, ElectiveChatGroup, DecodedPost
from database.models import ModerationRequest, ModerationStatus, Chat, IncomeRecord, Post
from handlers.users.place_advertisement_handler import get_message_text
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from middlewares.album_middleware import AlbumMiddleware, AlbumMedia
from utils.advertisement_sender import AdvertisementSender
from utils.validators.media_validator import MediaValidator
from utils.validators.str_validator import StringValidator
from utils.validators.int_validator import IntegerValidator
from forms.enums import PlacementTypes, AllowedContentTypes
from data.config import tools, AdminMenuReferences, meta
from aiogram.exceptions import TelegramBadRequest
from typing import Final, Dict, List, Union
from loader import bot, postgres, scheduler
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from data.texts import texts, templates
from database.enums import PostStatus
from states.states import StateGroup
from datetime import datetime
from aiogram import F, Router
import re


admin_router: Final[Router] = Router(name="admin")
message_input_router: Final[Router] = Router(name="messages")
message_input_router.message.middleware(AlbumMiddleware())
admin_router.include_router(message_input_router)


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
        now = datetime.now()
        month: int = now.month
        year: int = now.year
        posts: List[Post] = await postgres.get_month_posts(month)
        post_schedule: List[str] = [str(int(datetime.strftime(post.publish_date, "%Y-%m-%d")[-2:])) for post in posts]

        await call.message.edit_text(
            text="Календарь размещений",
            reply_markup=CalendarKeyboard(
                year=year,
                month=month,
                post_schedule=post_schedule
            ).get_keyboard(BackCallback(go_to="AdminMainMenu").pack())
        )
        admin_menu_references.TO_CALENDAR_MENU = call.data

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
        try:
            await bot.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id - 1
            )

        except TelegramBadRequest:
            pass

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
                chats: List[Chat] = [
                    await postgres.get_chat(chat_id=chat_id)
                    for chat_id in moderated_advertisement_form.advertisement_form.chats.chats
                ]
                chat_names: List[str] = [chat.chat_name for chat in chats]
                chat_name: str = str(chat_names).replace("[", "").replace("]", "")

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

        match = re.search(r"на (\d+) руб", call.message.text)
        total_sum: int = int(match.group(1))
        income_record: IncomeRecord = IncomeRecord(income_sum=total_sum)
        await postgres.add_income_record(income_record)

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


@admin_router.callback_query(DataPassCallback.filter(F.menu_level == CalendarKeyboard.get_menu_level()))
async def handle_calendar(call: CallbackQuery, state: FSMContext):
    callback_components: DataPassCallback = DataPassCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_admin_menu_references: str = state_data["admin_menu_references"]
    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)

    if callback_components.action == "next" or callback_components.action == "prev":
        year, month = callback_components.data.split("_")
        year, month = int(year), int(month)

        if callback_components.action == "next":
            if month == 12:
                year += 1
                month = 1

            else:
                month += 1

        elif callback_components.action == "prev":
            if month == 1:
                year -= 1
                month = 12

            else:
                month -= 1

        posts: List[Post] = await postgres.get_month_posts(month)
        post_schedule: List[str] = [str(int(datetime.strftime(post.publish_date, "%Y-%m-%d")[-2:])) for post in posts]

        await call.message.edit_reply_markup(
            reply_markup=CalendarKeyboard(
                year=year,
                month=month,
                post_schedule=post_schedule
            ).get_keyboard(BackCallback(go_to="AdminMainMenu").pack())
        )

    elif callback_components.action == "date":
        year, month, day = callback_components.data.split("-")

        year: int = int(year)
        month: int = int(month)
        day: int = int(day)

        posts: List[Post] = await postgres.get_posts_by_date(year, month, day)
        decoded_posts: List[DecodedPost] = [
            DecodedPost(
                id=post.id,
                job_id=post.job_id,
                status=post.status,
                publish_date=post.publish_date,
                post=await tools.deserializer.deserialize(post.post),
                chats=post.chats,
                message_ids=post.message_ids
            )
            for post in
            posts
        ]

        post_selection: PostSelectionKeyboard = PostSelectionKeyboard(decoded_posts)
        await call.message.edit_text(
            text=f"Список публикаций на {callback_components.data}",
            reply_markup=post_selection.get_keyboard(admin_menu_references.TO_CALENDAR_MENU)
        )

        admin_menu_references.TO_POST_SELECTION = call.data

        encoded_admin_menu_references: str = await tools.serializer.serialize(admin_menu_references)
        encoded_post_selection: str = await tools.serializer.serialize(post_selection)

        state_data["pagination"] = encoded_post_selection
        state_data["admin_menu_references"] = encoded_admin_menu_references
        await state.set_data(state_data)

    elif callback_components.action == "ignore":
        await call.answer(show_alert=True, text="Выберите день")


@admin_router.callback_query(DataPassCallback.filter(F.menu_level == PostSelectionKeyboard.get_menu_level()))
async def handle_post_selection(call: CallbackQuery, state: FSMContext):
    callback_components: DataPassCallback = DataPassCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_admin_menu_references: str = state_data["admin_menu_references"]
    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)

    if callback_components.action == "post":

        post_id: int = int(callback_components.data)
        post: Post = await postgres.get_post(post_id)
        decoded_post: DecodedPost = DecodedPost(
            id=post.id,
            job_id=post.job_id,
            status=post.status,
            publish_date=post.publish_date,
            post=await tools.deserializer.deserialize(post.post),
            chats=post.chats,
            message_ids=post.message_ids
        )

        text_to_show_limit: Final[int] = 50
        advertisement_sender: AdvertisementSender = AdvertisementSender()
        post_info: str = await advertisement_sender.get_post_info(decoded_post.post)\
                         + decoded_post.post.message.text[:text_to_show_limit]
        await call.message.edit_text(
            text=post_info,
            reply_markup=PostInteractionKeyboard(
                is_forward=decoded_post.post.message.is_forward
            ).get_keyboard(admin_menu_references.TO_POST_SELECTION)
        )

        admin_menu_references.TO_POST_INFO = call.data

        encoded_post: str = await tools.serializer.serialize(decoded_post)
        encoded_admin_menu_references: str = await tools.serializer.serialize(admin_menu_references)

        state_data["admin_menu_references"] = encoded_admin_menu_references
        state_data["current_post"] = encoded_post

        await state.set_data(state_data)
        await state.set_state(StateGroup.in_post_settings)

    else:
        await call.answer("Похоже что здесь пусто...")


@admin_router.callback_query(AdminCallback.filter(F.menu_level == PostInteractionKeyboard.get_menu_level()))
async def handle_post_interaction(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_admin_menu_references: str = state_data["admin_menu_references"]
    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)

    if callback_components.action == "modify":
        await call.message.edit_text(
            text=texts.get("modify_post"),
            reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_POST_INFO)
        )
        await state.set_state(StateGroup.in_post_modify)

    elif callback_components.action == "cancel_post":
        await call.message.edit_text(
            text=texts.get("post_cancellation_confirm"),
            reply_markup=PostCancellationConfirmKeyboard().get_keyboard(admin_menu_references.TO_POST_INFO)
        )


@admin_router.callback_query(AdminCallback.filter(F.menu_level == PostCancellationConfirmKeyboard.get_menu_level()))
async def handle_cancellation_confirm(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_post: str = state_data["current_post"]
    encoded_admin_menu_references: str = state_data["admin_menu_references"]

    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    if callback_components.action == "cancel":
        if post.status == PostStatus.deferred:
            scheduler.engine.remove_job(post.job_id)
            await postgres.delete_post(post.id)

        await call.message.edit_text(
            text="Пост был успешно отменен!✅",
            reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_POST_SELECTION)
        )


@message_input_router.message(StateFilter(StateGroup.in_post_modify))
async def handle_write_message_to_place(message: Message, state: FSMContext, album: List[AlbumMedia] = None):
    state_data: Dict = await state.get_data()

    encoded_post: str = state_data["current_post"]
    encoded_admin_menu_references: str = state_data["admin_menu_references"]

    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    media_validator: MediaValidator = MediaValidator()
    placement_type: PlacementTypes = post.post.placement_type
    got_message: bool = True

    if placement_type == PlacementTypes.message_from_bot:
        post.post.message.is_forward = False
        post.post.message.album = []
        post.post.message.is_document = False

        if album:
            max_text_length: int = 900
            post.post.message.album = album

        elif media_validator.has_media(message):
            max_text_length: int = 900
            is_valid: bool = media_validator.validate(message)

            if is_valid:

                if message.photo:
                    post.post.message.album.append(
                        AlbumMedia(photo=message.photo[-1].file_id, caption=message.caption)
                    )

                elif message.video:
                    post.post.message.album.append(
                        AlbumMedia(video=message.video.file_id, caption=message.caption)
                    )

                elif message.document is not None:
                    post.post.message.is_document = True
                    post.post.message.document = message.document.file_id

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
                post.post.message.text = text

            else:
                got_message: bool = False
                await message.answer(
                    """
                    Ваше сообщение слишком большое ❌\nПожалуйста убедитесь в том, 
                    что ваше сообщение соответствует требованиям выше.
                    """
                )
        else:
            post.post.message.text = text

        has_media: bool = len(post.post.message.album) != 0

    else:
        post.post.message.is_forward = True
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
            post.post.message.message_id = message.message_id
            post.post.message.text = message.text
        has_media: bool = False

    encoded_post: str = await tools.serializer.serialize(post)
    state_data["current_post"] = encoded_post
    await state.set_data(state_data)

    final_keyboard: PostModifyKeyboard = \
        PostModifyKeyboard(
            has_media=has_media,
            is_document=post.post.message.is_document
        )

    if got_message:
        await message.answer(
            text=texts.get("check_post_details").format(text=post.post.message.text),
            reply_markup=final_keyboard.get_keyboard(admin_menu_references.TO_POST_INFO)
        )

        await state.set_state(StateGroup.place_advertisement)

    else:
        return None


@admin_router.callback_query(AdminCallback.filter(F.menu_level == PostModifyKeyboard.get_menu_level()))
async def handle_post_modify(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()
    encoded_post: str = state_data["current_post"]
    encoded_admin_menu_references: str = state_data["admin_menu_references"]

    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    if callback_components.action == "complete":
        if bool(post.post.message.text) or \
                bool(post.post.message.album):

            encoded_post_material: str = await tools.serializer.serialize(post.post)
            await postgres.change_post_materials(post.id, encoded_post_material)

            await call.answer(text="Изменения прошли успешно! ", show_alert=True)
            await call.message.edit_text(
                text="Изменения прошли успешно!✅",
                reply_markup=InlineBuilder().get_back_button_keyboard(admin_menu_references.TO_POST_SELECTION)
            )

        else:
            await call.answer("❌ Ошибка!\nВаше сообщение пустое!")

    elif callback_components.action == "pin_modify":
        admin_menu_references.TO_PIN_TIME_SELECTION = call.data
        await call.message.edit_text(
            text=texts.get("select_pin_time"),
            reply_markup=AdminPinTimeSelectionBuilder().get_keyboard(BackCallback(go_to="complete_keyboard"))
        )

    elif callback_components.action == "attach_media":
        await call.message.edit_text(
            text=texts.get("attach_media_text"),
            reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard"))
        )
        await state.set_state(StateGroup.write_attach_media)

    elif callback_components.action == "delete_all_media":
        post.post.message.album = []
        post.post.message.document = None
        post.post.message.is_document = None
        await call.answer(show_alert=True, text="Все медиа файлы успешно удалены!")
        await call.message.edit_reply_markup(
            reply_markup=PostModifyKeyboard(
                 has_media=False
            ).get_keyboard(admin_menu_references.TO_POST_INFO)
        )

    encoded_admin_menu_references: str = await tools.serializer.serialize(admin_menu_references)
    encoded_post: str = await tools.serializer.serialize(post)

    state_data["admin_menu_references"] = encoded_admin_menu_references
    state_data["current_post"] = encoded_post
    await state.set_data(state_data)


@admin_router.callback_query(
    BackCallback.filter(F.go_to == "complete_keyboard"),
)
async def handle_back_from_attach_media(msg: Union[CallbackQuery, Message], state: FSMContext):
    state_data: Dict = await state.get_data()
    encoded_post: str = state_data["current_post"]
    encoded_admin_menu_references: str = state_data["admin_menu_references"]

    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    has_media: bool = len(post.post.message.album) != 0

    final_keyboard: PostModifyKeyboard = \
        PostModifyKeyboard(
            has_media=has_media,
            is_document=post.post.message.is_document
        )

    if isinstance(msg, CallbackQuery):
        await msg.message.edit_text(
            text=texts.get("check_post_details").format(text=post.post.message.text),
            reply_markup=final_keyboard.get_keyboard(admin_menu_references.TO_POST_INFO)
        )

    else:
        await msg.delete()
        message_to_delete = await msg.answer(
            text="Загрузка...",
            reply_markup=ReplyKeyboardRemove()
        )
        await message_to_delete.delete()
        await msg.answer(
            text=texts.get("check_post_details").format(text=post.post.message.text),
            reply_markup=final_keyboard.get_keyboard(admin_menu_references.TO_POST_INFO)
        )

    await state.set_state(StateGroup.place_advertisement)


@message_input_router.message(StateFilter(StateGroup.write_attach_media))
async def handle_attach_media(message: Message, state: FSMContext, album: List[AlbumMedia] = None):
    state_data: Dict = await state.get_data()
    encoded_post: str = state_data["current_post"]
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    str_validator: StringValidator = StringValidator()

    text: str = await get_message_text(message, album)
    got_message: bool = False

    is_valid = str_validator.validate(text)

    if is_valid:
        if album:
            post.post.message.album += album
            got_message = True

        else:
            if message.content_type != AllowedContentTypes.video.value \
                    and message.content_type != AllowedContentTypes.photo.value:

                await message.answer("❌ Ошибка! \nФайл должен быть либо фото, либо видео")
                await message.delete()

            else:
                if message.photo:
                    post.post.message.album.append(
                        AlbumMedia(photo=message.photo[-1].file_id, caption=message.caption)
                    )

                elif message.video:
                    post.post.message.album.append(
                        AlbumMedia(video=message.video.file_id, caption=message.caption)
                    )

                got_message = True

        if post.post.message.text is not None:
            post.post.message.album[0].caption = post.post.message.text

    else:
        await message.answer("❌ Ошибка!\nФайл должен быть отправлен без текста!")
        await message.delete()

    if got_message:
        await message.answer(
            text="Принято!✅\nВы можете продолжить, либо вернуться ",
            reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard"))
        )

    encoded_post: str = await tools.serializer.serialize(post)
    state_data["current_post"] = encoded_post
    await state.set_data(state_data)


@admin_router.callback_query(
    AdminCallback.filter(F.menu_level == AdminPinTimeSelectionBuilder.get_menu_level()),
)
async def handle_pin_time_selection(call: CallbackQuery, state: FSMContext):
    callback_components: AdminCallback = AdminCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_post: str = state_data["current_post"]
    encoded_admin_menu_references: str = state_data["admin_menu_references"]

    admin_menu_references: AdminMenuReferences = await tools.deserializer.deserialize(encoded_admin_menu_references)
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    if callback_components.action == "write_days_count":
        await call.message.edit_text(
            text=texts.get("enter_number_of_pin_days"),
            reply_markup=InlineBuilder().get_back_button_keyboard(
                back_callback=admin_menu_references.TO_PIN_TIME_SELECTION
            )
        )
        await state.set_state(StateGroup.write_pin_days_count)

    elif callback_components.action.isnumeric():
        pin_days: Final[int] = int(callback_components.action)
        post.post.pin_days = pin_days
        if pin_days == 0:
            text: str = "Вы выбрали размещение без закрепления ✅"

        else:
            text: str = f"Вы выбрали закреп на {pin_days} дня / дней ✅"

        await call.answer(text=text)

        await call.message.edit_text(
            text=text,
            reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard"))
        )

    encoded_admin_menu_references: str = await tools.serializer.serialize(admin_menu_references)
    encoded_post: str = await tools.serializer.serialize(post)

    state_data["admin_menu_references"] = encoded_admin_menu_references
    state_data["current_post"] = encoded_post
    await state.set_data(state_data)


@admin_router.message(
    StateFilter(StateGroup.write_pin_days_count)
)
async def handle_write_pin_days_count(message: Message, state: FSMContext):
    state_data: Dict = await state.get_data()

    encoded_post: str = state_data["current_post"]
    post: DecodedPost = await tools.deserializer.deserialize(encoded_post)

    int_validator: IntegerValidator = IntegerValidator(
        max_possible_value=meta.MAX_PIN_DAYS_POSSIBLE
    )

    is_valid, value = int_validator.validate(message.text)

    if is_valid:
        post.post.pin_days = value
        await message.answer(
            text=f"Вы выбрали закреп на {value} дня / дней ✅",
            reply_markup=InlineBuilder().get_back_button_keyboard(BackCallback(go_to="complete_keyboard"))
        )

    else:
        await message.answer("❌Количество дней не должно быть больше 31!")
        await message.delete()

    await message.delete()
    await state.set_state(StateGroup.in_post_settings)

    encoded_post: str = await tools.serializer.serialize(post)
    state_data["current_post"] = encoded_post
    await state.set_data(state_data)



