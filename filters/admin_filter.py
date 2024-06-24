from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter
from typing import Final, Union
from data.config import config
from redis import Redis


class AdminFilter(BaseFilter):

    def __init__(self):
        redis: Redis = Redis.from_url(url=config.REDIS_URL)
        self.__admin_id: Final[Union[str, int]] = bytes.decode(redis.get("admin"))
        redis.close()

    async def __call__(self, obj) -> bool:
        if isinstance(obj, Message):
            return obj.from_user.id == self.__admin_id
        elif isinstance(obj, CallbackQuery):
            return obj.from_user.id == self.__admin_id
        return False

