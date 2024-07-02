from keyboards.inline.admin_keyboards import AdminModerationKeyboard
from aiogram.types import InputMediaPhoto, InputMediaVideo, Message
from forms.forms import PlaceAdvertisementForm, MessageToPlaceForm
from keyboards.inline.callbacks import BackCallback
from loader import bot, postgres, scheduler
from forms.forms import ElectiveChatGroup
from datetime import datetime, timedelta
from forms.enums import PlacementTypes
from database.enums import PostStatus
from typing import Union, Final, List
from database.models import Chat
from data.texts import templates
from data.config import tools
from data.texts import texts


class AdvertisementSender:

    async def unpin_chat_message(self, chat_id: int, message_id: int):
        await bot.unpin_chat_message(chat_id, message_id)

    async def __setup_unpin_message_task(
            self, place_advertisement_form: PlaceAdvertisementForm,
            chat_id: int, message_id: int
    ):
        date = place_advertisement_form.date
        time = place_advertisement_form.time

        task_datetime = datetime.strptime(
            f'{date} {time}',
            '%Y-%m-%d %H:%M'
        ) + timedelta(days=place_advertisement_form.pin_days)

        scheduler.engine.add_job(
            func=self.unpin_chat_message,
            trigger="date",
            run_date=task_datetime,
            coalesce=True,
            args=(chat_id, message_id)
        )

    async def __send_media_group(self, chat_id: int, message: MessageToPlaceForm) -> Message:
        media = [
            InputMediaVideo(media=media.video, caption=media.caption)
            if media.video else
            InputMediaPhoto(media=media.photo, caption=media.caption)
            for media in message.album
        ]

        sent_message: Message = await bot.send_media_group(
            chat_id=chat_id,
            media=media
        )
        return sent_message

    async def __send_document(self, chat_id: int, message: MessageToPlaceForm) -> Message:
        sent_message: Message = await bot.send_document(
            chat_id=chat_id,
            document=message.document,
            caption=message.text
        )
        return sent_message

    async def __send_only_text(self, chat_id: int, message: MessageToPlaceForm) -> Message:
        sent_message: Message = await bot.send_message(
            chat_id=chat_id,
            text=message.text
        )
        return sent_message

    async def __forward_message(self, chat_id: int, message: MessageToPlaceForm) -> Message:
        sent_message: Message = await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=message.from_user.id,
            message_id=message.message_id
        )
        return sent_message

    async def __convert_to_form_object(self, place_advertisement_form: str):
        place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
            place_advertisement_form
        )
        return place_advertisement_form

    async def __extract_chat_names(self, chat_ids: List[Union[str, int]]) -> List[Chat]:
        chats: List[Chat] = [await postgres.get_chat(chat_id=chat_id) for chat_id in chat_ids]
        return [chat.chat_name for chat in chats]

    async def get_post_info(self, place_advertisement_form: PlaceAdvertisementForm):
        if isinstance(place_advertisement_form.chats, ElectiveChatGroup):
            if place_advertisement_form.chats.all_city:
                chat_names: str = "<b>Весь город</b>"

            else:
                chat_ids: List = place_advertisement_form.chats.chats

                chat_names: List[str] = await self.__extract_chat_names(chat_ids)
                chat_names: str = str(chat_names).replace("[", "").replace("]", "")

        else:
            chat_names: str = place_advertisement_form.chats.name

        empty_template: str = templates.get("post_info")
        filled_template = empty_template.format(
            username=place_advertisement_form.message.from_user.username,
            date=place_advertisement_form.date,
            time=place_advertisement_form.time,
            pin_days=place_advertisement_form.pin_days,
            chats=chat_names,
        )
        return filled_template

    async def __get_method(self, place_advertisement_form: PlaceAdvertisementForm):
        if place_advertisement_form.placement_type == PlacementTypes.message_from_bot:
            if place_advertisement_form.message.album:
                return self.__send_media_group

            elif place_advertisement_form.message.is_document:
                return self.__send_document

            else:
                return self.__send_only_text

        else:
            return self.__forward_message

    async def place_advertisement(self, post_id: int):
        post = await postgres.get_post(post_id)
        place_advertisement_form = await self.__convert_to_form_object(post.post)

        send = await self.__get_method(place_advertisement_form)

        messages_ids: List[int] = []

        if place_advertisement_form.pin_days > 0:
            for chat_id in place_advertisement_form.chats.chats:
                chat_id: int = int("-100" + chat_id)
                sent_message: Message = await send(chat_id, place_advertisement_form.message)

                if isinstance(sent_message, list):
                    await bot.pin_chat_message(
                        chat_id=sent_message[0].chat.id,
                        message_id=sent_message[0].message_id,
                    )

                    await self.__setup_unpin_message_task(
                        place_advertisement_form=place_advertisement_form,
                        chat_id=chat_id,
                        message_id=sent_message[0].message_id
                    )
                    messages_ids.append(sent_message[0].message_id)

                else:
                    await bot.pin_chat_message(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                    )

                    await self.__setup_unpin_message_task(
                        place_advertisement_form=place_advertisement_form,
                        chat_id=chat_id,
                        message_id=sent_message.message_id
                    )
                    messages_ids.append(sent_message.message_id)

        else:
            for chat_id in place_advertisement_form.chats.chats:
                chat_id: int = int("-100" + chat_id)
                sent_message: Message = await send(chat_id, place_advertisement_form.message)
                messages_ids.append(sent_message.message_id)

        await postgres.add_messages_ids(post_id, messages_ids)
        await postgres.change_post_status(post_id, PostStatus.placed)
        await postgres.delete_job_id(post_id)

    async def send_advertisement(
            self,
            chat_id: Union[str, int],
            place_advertisement_form: Union[PlaceAdvertisementForm, str],
    ):

        if isinstance(place_advertisement_form, str):
            place_advertisement_form = await self.__convert_to_form_object(place_advertisement_form)

        send = await self.__get_method(place_advertisement_form)
        await send(chat_id, place_advertisement_form.message)

    async def send_to_admin_on_moderation(
            self,
            place_advertisement_form: Union[str, PlaceAdvertisementForm],
            admin_id: Union[str, int],
    ):

        if isinstance(place_advertisement_form, str):
            place_advertisement_form = await self.__convert_to_form_object(place_advertisement_form)

        moderation_info: str = "Объявление на модерацию:\n" + await self.get_post_info(
            place_advertisement_form=place_advertisement_form
        )

        await self.send_advertisement(
            chat_id=admin_id,
            place_advertisement_form=place_advertisement_form,
        )

        moderation_keyboard: Final[AdminModerationKeyboard] = AdminModerationKeyboard()
        await bot.send_message(
            chat_id=admin_id,
            text=moderation_info + texts.get("request_admin_moderation_decision"),
            reply_markup=moderation_keyboard.get_keyboard(BackCallback(go_to="AdminMainMenu").pack())
        )

        del moderation_keyboard
