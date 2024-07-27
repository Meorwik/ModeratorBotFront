from keyboards.inline.keyboards import SelectPaymentMethodKeyboard, PaymentProviderKeyboard, \
    InlineBuilder, PaymentCheckResultKeyboard
from keyboards.inline.callbacks import ActionCallback, DataPassCallback
from keyboards.inline.admin_keyboards import AcceptPaymentKeyboard
from data.config import meta, config
from utils.advertisement_sender import AdvertisementSender
from keyboards.default.keyboards import WebAppKeyboard
from database.models import ModerationRequest, Post
from forms.forms import ModeratedAdvertisementForm
from aiogram.types import CallbackQuery, Message
from forms.enums import AllowedCheckContentTypes
from aiogram.types import ReplyKeyboardRemove
from utils.price_counter import PriceCounter
from database.enums import ModerationStatus
from loader import postgres, bot, scheduler
from aiogram.fsm.context import FSMContext
from data.texts import templates, texts
from aiogram.filters import StateFilter
from states.states import StateGroup
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

    placement_service_cost: Final[int] = await price_counter.get_placement_service_cost()
    pin_service_cost: Final[int] = await price_counter.get_pin_service_cost()
    total_cost: Final[int] = await price_counter.count_price()

    services_cost_check: Final[str] = \
        templates["service_cost_check"].format(service_name="Размещение", service_cost=placement_service_cost) +\
        templates["service_cost_check"].format(service_name="Закрепление", service_cost=pin_service_cost)

    payment_check: Final[str] = templates.get("payment_check_text").format(
        services_cost_check=services_cost_check, total_cost=total_cost, card_number=meta.CARD_NUMBER
    )

    if callback_components.action == "entity":
        await call.message.edit_text(
            text=payment_check,
            reply_markup=PaymentProviderKeyboard(
                is_entity=True, advertisement_form=str(moderated_advertisement_form.request_id)
            ).get_keyboard()
        )
        encoded_moderated_advertisement_form: str = await tools.serializer.serialize(moderated_advertisement_form)
        state_data["moderated_advertisement_form"] = encoded_moderated_advertisement_form

    elif callback_components.action == "individual":
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

    if callback_components.action == "paid":
        await call.message.edit_text(texts.get("request_payment_check"))
        await state.set_state(StateGroup.write_payment_check)


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
    encoded_moderated_advertisement_form: str = state_data["moderated_advertisement_form"]
    moderated_advertisement_form: ModeratedAdvertisementForm = await tools.deserializer.deserialize(
        encoded_moderated_advertisement_form
    )

    if callback_components.action == "change_datetime":
        await call.message.delete()
        await call.message.answer(
            text=texts.get("choose_publish_datetime"),
            reply_markup=WebAppKeyboard().get_keyboard_webapp_only()
        )
        await state.set_state(StateGroup.write_datetime_web_data_payment_stage)

    elif callback_components.action == "confirm":
        await call.message.edit_text(
            text=texts.get("finish_payment"),
            reply_markup=InlineBuilder().get_keyboard()
        )

        await state.clear()

        await schedule_post_publication(moderated_advertisement_form)


@payment_router.message(
    F.web_app_data,
    StateFilter(StateGroup.write_datetime_web_data_payment_stage)
)
async def handle_datetime_choice(message: Message, state: FSMContext):
    state_data: Dict = await state.get_data()

    datetime_separator: Final[str] = ";"
    date, time = message.web_app_data.data.split(datetime_separator)

    encoded_moderated_advertisement_form: str = state_data["moderated_advertisement_form"]
    moderated_advertisement_form: ModeratedAdvertisementForm = await tools.deserializer.deserialize(
        encoded_moderated_advertisement_form
    )

    moderated_advertisement_form.advertisement_form.date = date
    moderated_advertisement_form.advertisement_form.time = time

    message_to_delete = await message.answer(
        text="Загрузка...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message_to_delete.delete()

    await message.answer(
        text=texts.get("finish_all_stages"),
        reply_markup=InlineBuilder().get_keyboard()
    )
    await state.clear()

    await schedule_post_publication(moderated_advertisement_form)




