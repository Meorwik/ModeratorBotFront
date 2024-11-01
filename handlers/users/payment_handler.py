from handlers.users.main_menu import reopen_main_menu
from keyboards.inline.keyboards import SelectPaymentMethodKeyboard, PaymentProviderKeyboard, \
    InlineBuilder, PaymentCheckResultKeyboard, FinalKeyboard
from keyboards.inline.callbacks import ActionCallback, DataPassCallback
from keyboards.inline.admin_keyboards import AcceptPaymentKeyboard
from utils.advertisement_sender import AdvertisementSender
from database.models import ModerationRequest, Post
from forms.forms import ModeratedAdvertisementForm
from aiogram.types import CallbackQuery, Message
from forms.enums import AllowedCheckContentTypes
from utils.price_counter import PriceCounter
from database.enums import ModerationStatus
from loader import postgres, bot, scheduler
from aiogram.fsm.context import FSMContext
from data.texts import templates, texts
from aiogram.filters import StateFilter
from data.config import MenuReferences
from states.states import StateGroup
from data.config import config
from typing import Final, Dict
from datetime import datetime
from data.config import tools
from aiogram import Router, F
from redis import Redis


async def schedule_post_publication(moderated_advertisement_form):
    advertisement_sender: AdvertisementSender = AdvertisementSender()
    date = moderated_advertisement_form.advertisement_form.date
    time = moderated_advertisement_form.advertisement_form.time

    task_datetime = datetime.strptime(
        f'{date} {time}',
        '%Y-%m-%d %H:%M'
    )

    encoded_advertisement_form: str = await tools.serializer.serialize(moderated_advertisement_form.advertisement_form)
    publish_date = datetime.strptime(moderated_advertisement_form.advertisement_form.date, '%Y-%m-%d')
    post: Post = Post(
        publish_date=publish_date,
        post=encoded_advertisement_form,
        chats=[int(chat_id) for chat_id in moderated_advertisement_form.advertisement_form.chats.chats],
    )
    post: Post = await postgres.add_post(post)

    job = scheduler.engine.add_job(
        func=advertisement_sender.place_advertisement,
        trigger="date",
        run_date=task_datetime,
        coalesce=True,
        args=(
            post.id,
        )
    )

    await postgres.add_job_id(post_id=post.id, job_id=job.id)


payment_router: Final[Router] = Router(name="payment")


@payment_router.callback_query(DataPassCallback.filter(F.menu_level == SelectPaymentMethodKeyboard.get_menu_level()))
async def handle_payment_method_selection(call: CallbackQuery, state: FSMContext):
    callback_components: DataPassCallback = DataPassCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    moderation_request: ModerationRequest = await postgres.get_moderation_request_by_id(int(callback_components.data))
    moderated_advertisement_form: ModeratedAdvertisementForm = ModeratedAdvertisementForm(
        request_id=moderation_request.id,
        advertisement_form=await tools.deserializer.deserialize(moderation_request.form)
    )

    price_counter: PriceCounter = PriceCounter(moderated_advertisement_form.advertisement_form)
    total_cost: Final[int] = await price_counter.count_price()

    date: str = moderated_advertisement_form.advertisement_form.date
    time: str = moderated_advertisement_form.advertisement_form.time
    chats: str = moderated_advertisement_form.advertisement_form.chats.name

    if chats is None:
        chats = "Свой пакет"
    pin_days: int = moderated_advertisement_form.advertisement_form.pin_days

    payment_check: Final[str] = templates.get("payment_check_text").format(
        total=total_cost, date=date, time=time, chats=chats, pin_days=pin_days
    )


    if callback_components.action == "individual":
        encoded_menu_references: str = state_data["menu_references"]
        menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)
        menu_references.TO_PAYMENT_APPROVAL = call.data
        state_data["menu_references"] = await tools.serializer.serialize(menu_references)

        await call.message.edit_text(
            text=payment_check,
            reply_markup=PaymentProviderKeyboard(
                is_entity=False, advertisement_form=str(moderated_advertisement_form.request_id)
            ).get_keyboard()
        )

        encoded_moderated_advertisement_form: str = await tools.serializer.serialize(moderated_advertisement_form)
        state_data["moderated_advertisement_form"] = encoded_moderated_advertisement_form

    elif callback_components.action == "cancel_request":
        redis: Redis = Redis.from_url(url=config.REDIS_URL)
        admin_id = redis.get("admin")
        redis.close()

        await postgres.change_moderation_request_status(moderation_request.id, ModerationStatus.canceled)
        await bot.send_message(
            chat_id=admin_id,
            text=templates.get("canceled_post_text").format(username=call.from_user.username)
        )

        await call.message.edit_text(
            text="🗑Ваш пост успешно отменён!",
            reply_markup=InlineBuilder(level="deleted_post").get_keyboard()
        )

    await state.set_data(state_data)
    await state.set_state(StateGroup.in_payment_stage)


@payment_router.callback_query(ActionCallback.filter(F.menu_level == PaymentProviderKeyboard.get_menu_level()))
async def handle_provided_payment_method(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    encoded_moderated_advertisement_form: str = state_data["moderated_advertisement_form"]
    moderated_advertisement_form: ModeratedAdvertisementForm = await tools.deserializer.deserialize(
        encoded_moderated_advertisement_form
    )

    if callback_components.action == "paid":
        encoded_menu_references: str = state_data["menu_references"]
        menu_references: MenuReferences = await tools.deserializer.deserialize(encoded_menu_references)

        await call.message.edit_text(
            text=texts.get("request_payment_check"),
            reply_markup=InlineBuilder().get_back_button_keyboard(menu_references.TO_PAYMENT_APPROVAL)
        )
        await state.set_state(StateGroup.write_payment_check)

    elif callback_components.action == "to_successfully_moderated_msg":
        await call.message.edit_text(
            text=templates.get("approved_post_text").format(total_cost=moderated_advertisement_form.advertisement_form.total_cost),
            reply_markup=SelectPaymentMethodKeyboard(moderated_advertisement_form.request_id).get_keyboard()
        )

    elif callback_components.action == "retry":
        ...


@payment_router.message(StateFilter(StateGroup.write_payment_check))
async def handle_write_payment_check(message: Message, state: FSMContext):
    state_data: Dict = await state.get_data()

    encoded_moderated_advertisement_form: str = state_data["moderated_advertisement_form"]
    moderated_advertisement_form: ModeratedAdvertisementForm = await tools.deserializer.deserialize(
        encoded_moderated_advertisement_form
    )

    if message.content_type == AllowedCheckContentTypes.photo.value or \
            message.content_type == AllowedCheckContentTypes.document.value:

        redis: Redis = Redis.from_url(url=config.REDIS_URL)
        admin_id = redis.get("admin")
        redis.close()

        await message.forward(admin_id)
        await bot.send_message(
            chat_id=admin_id,
            text=templates.get("user_confirmed_payment").format(
                username=moderated_advertisement_form.advertisement_form.message.from_user.username,
                total_cost=moderated_advertisement_form.advertisement_form.total_cost
            ),
            reply_markup=AcceptPaymentKeyboard(
                request_id=moderated_advertisement_form.request_id
            ).get_keyboard()
        )

        await message.answer(
            text=texts.get("admin_checks_payment_text")
        )
        await state.set_state(None)

    else:
        await message.answer(
            text="❌Ошибка!\nПринимается только документ или фотография"
        )
        await message.delete()

    encoded_moderated_advertisement_form: str = await tools.serializer.serialize(moderated_advertisement_form)
    state_data["moderated_advertisement_form"] = encoded_moderated_advertisement_form
    await state.set_data(state_data)


@payment_router.callback_query(ActionCallback.filter(F.menu_level == PaymentCheckResultKeyboard.get_menu_level()))
async def handle_payment_check_result(call: CallbackQuery, state: FSMContext):
    callback_components: ActionCallback = ActionCallback.unpack(call.data)
    state_data: Dict = await state.get_data()

    if callback_components.action == "confirm":
        encoded_moderated_advertisement_form: str = state_data["moderated_advertisement_form"]
        moderated_advertisement_form: ModeratedAdvertisementForm = await tools.deserializer.deserialize(
            encoded_moderated_advertisement_form
        )

        await call.message.edit_text(
            text=texts.get("finish_payment"),
            reply_markup=FinalKeyboard().get_keyboard()
        )

        await state.clear()
        await schedule_post_publication(moderated_advertisement_form)

    elif callback_components.action == "restart":
        await reopen_main_menu(call)



