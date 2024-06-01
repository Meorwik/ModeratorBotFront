from typing import Final
from enum import Enum


class PlacementTypes(Enum):
    group_repost: Final[str] = "group_repost"
    direct_messages_repost: Final[str] = "direct_messages_repost"
    message_from_bot: Final[str] = "message_from_bot"

    @classmethod
    def get_type(cls, option_number: int):
        if option_number == 1:
            return cls.message_from_bot

        elif option_number == 2:
            return cls.group_repost

        elif option_number == 3:
            return cls.direct_messages_repost


class PaginationActionTypes(Enum):
    open_next_page: Final[str] = "open_next_page"
    open_previous_page: Final[str] = "open_previous_page"


class PlacementTypesMediaPaths(Enum):
    FROM_BOT: Final[str] = "data/media/placement_types/from_bot.jpg"
    FROM_GROUP: Final[str] = "data/media/placement_types/from_group.jpg"
    FROM_USER: Final[str] = "data/media/placement_types/from_user.jpg"

    @classmethod
    def get_picture(cls, option_number: int):
        if option_number == 1:
            return cls.FROM_BOT

        elif option_number == 2:
            return cls.FROM_GROUP

        elif option_number == 3:
            return cls.FROM_USER


