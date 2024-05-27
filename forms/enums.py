from typing import Final
from enum import Enum


class PlacementTypes(Enum):
    group_repost: Final[str] = "group_repost"
    direct_messages_repost: Final[str] = "direct_messages_repost"
    message_from_bot: Final[str] = "message_from_bot"


class PaginationActionTypes(Enum):
    open_next_page: Final[str] = "open_next_page"
    open_previous_page: Final[str] = "open_previous_page"

