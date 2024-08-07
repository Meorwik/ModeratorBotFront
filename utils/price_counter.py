from forms.forms import PlaceAdvertisementForm
from forms.forms import ElectiveChatGroup
from database.models import ChatGroup
from data.config import price_meta
from typing import Final, List
from loader import postgres


class PriceCounter:

    def __init__(self, place_advertisement_form: PlaceAdvertisementForm):
        self.__form: Final[PlaceAdvertisementForm] = place_advertisement_form

    async def __count_all_chats(self):
        price: int = self.__form.pin_days * price_meta.ONE_DAY_PIN_FOR_ALL_CHATS + price_meta.ALL_CHATS
        return price

    async def __count_elective_chat_group(self, chat_group: ElectiveChatGroup):
        chats: List[int] = chat_group.chats
        price: int = len(chats) * price_meta.ONE_CHAT + self.__form.pin_days * price_meta.ONE_DAY_PIN_FOR_ONE_CHAT
        return price

    async def __count_chat_group(self, chat_group_id: int):
        chat_group: ChatGroup = await postgres.get_chat_group(chat_group_id)
        price: int = chat_group.cost_of_placement + chat_group.cost_of_one_day_pin * self.__form.pin_days
        return price

    async def count_price(self) -> int:
        if isinstance(self.__form.chats, ElectiveChatGroup):
            if self.__form.chats.all_city:
                return await self.__count_all_chats()

            else:
                return await self.__count_elective_chat_group(self.__form.chats)

        elif isinstance(self.__form.chats, ChatGroup):
            return await self.__count_chat_group(self.__form.chats.id)

    async def get_placement_service_cost(self) -> int:
        if isinstance(self.__form.chats, ElectiveChatGroup):
            if self.__form.chats.all_city:
                return price_meta.ALL_CHATS

            else:
                return price_meta.ONE_CHAT * len(self.__form.chats.chats)

        elif isinstance(self.__form.chats, ChatGroup):
            return self.__form.chats.cost_of_placement

    async def get_pin_service_cost(self) -> int:
        if isinstance(self.__form.chats, ElectiveChatGroup):
            if self.__form.chats.all_city:
                return price_meta.ONE_DAY_PIN_FOR_ALL_CHATS * self.__form.pin_days

            else:
                return price_meta.ONE_DAY_PIN_FOR_ONE_CHAT * self.__form.pin_days

        elif isinstance(self.__form.chats, ChatGroup):
            return self.__form.chats.cost_of_one_day_pin * self.__form.pin_days

