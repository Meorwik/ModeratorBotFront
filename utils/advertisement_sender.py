from forms.forms import PlaceAdvertisementForm
from forms.enums import PlacementTypes
from aiogram.types import InputMediaPhoto, InputMediaVideo, User
from keyboards.inline.callbacks import BackCallback
from forms.forms import ElectiveChatGroup
from database.models import ChatGroup, Chat
from keyboards.inline.admin_keyboards import AdminModerationKeyboard
from data.texts import texts
from loader import bot, postgres
from data.texts import templates
from data.config import tools
from typing import Union, Final, List


class AdvertisementSender:

    async def send_advertisement(
            self,
            chat_id: Union[str, int],
            place_advertisement_form: Union[PlaceAdvertisementForm, str],
            text: str = None
    ):

        if isinstance(place_advertisement_form, str):
            place_advertisement_form = await self.__convert_to_form_object(place_advertisement_form)

        if place_advertisement_form.placement_type == PlacementTypes.message_from_bot:
            if place_advertisement_form.message.album:
                media = [
                    InputMediaVideo(media=media.video, caption=media.caption)
                    if media.video else
                    InputMediaPhoto(media=media.photo, caption=media.caption)
                    for media in place_advertisement_form.message.album
                ]
                if text:
                    media[0].caption = text

                await bot.send_media_group(
                    chat_id=chat_id,
                    media=media
                )

            elif place_advertisement_form.message.is_document:
                if text:
                    caption: str = text

                else:
                    caption: str = place_advertisement_form.message.text

                await bot.send_document(
                    chat_id=chat_id,
                    document=place_advertisement_form.message.document,
                    caption=caption
                )

            else:
                if text:
                    caption: str = text

                else:
                    caption: str = place_advertisement_form.message.text

                await bot.send_message(
                    chat_id=chat_id,
                    text=caption
                )

        else:
            await bot.forward_message(
                chat_id=chat_id,
                from_chat_id=place_advertisement_form.message.from_user.id,
                message_id=place_advertisement_form.message.message_id
            )

    async def __convert_to_form_object(self, place_advertisement_form: str):
        place_advertisement_form: PlaceAdvertisementForm = await tools.deserializer.deserialize(
            place_advertisement_form
        )
        return place_advertisement_form

    async def __extract_chat_names(self, chat_ids: List[Union[str, int]]) -> List[Chat]:
        chats: List[Chat] = [await postgres.get_chat(chat_id=chat_id) for chat_id in chat_ids]
        return [chat.chat_name for chat in chats]

    async def __add_moderator_text(self, place_advertisement_form: PlaceAdvertisementForm):
        chat_ids: List = place_advertisement_form.chats.chats

        chat_names: List[str] = await self.__extract_chat_names(chat_ids)
        chat_names: str = str(chat_names).replace("[", "").replace("]", "")

        empty_template: str = templates.get("moderation_text")
        filled_template = empty_template.format(
            username=place_advertisement_form.message.from_user.username,
            date=place_advertisement_form.date,
            time=place_advertisement_form.time,
            pin_days=place_advertisement_form.pin_days,
            chats=chat_names,
        )
        return filled_template

    async def send_to_admin_on_moderation(
            self,
            place_advertisement_form: Union[str, PlaceAdvertisementForm],
            admin_id: Union[str, int],
    ):

        if isinstance(place_advertisement_form, str):
            place_advertisement_form = await self.__convert_to_form_object(place_advertisement_form)

        moderation_info: str = await self.__add_moderator_text(
            place_advertisement_form=place_advertisement_form
        )

        await self.send_advertisement(
            chat_id=admin_id,
            place_advertisement_form=place_advertisement_form,
            text=moderation_info + place_advertisement_form.message.text
        )

        moderation_keyboard: Final[AdminModerationKeyboard] = AdminModerationKeyboard()
        await bot.send_message(
            chat_id=admin_id,
            text=texts.get("request_admin_moderation_decision"),
            reply_markup=moderation_keyboard.get_keyboard(BackCallback(go_to="AdminMainMenu").pack())
        )
        del moderation_keyboard
