from data.texts import texts, templates
from aiogram.types import ContentType
from .base import BasePlacementTypes
from typing import Final
from enum import Enum


class PlacementTypes(BasePlacementTypes, Enum):
    group_repost: Final[str] = "group_repost"
    direct_messages_repost: Final[str] = "direct_messages_repost"
    message_from_bot: Final[str] = "message_from_bot"


class PlacementTypesNames(BasePlacementTypes, Enum):
    group_repost: Final[str] = "Репост из группы"
    direct_messages_repost: Final[str] = "Репост из переписки"
    message_from_bot: Final[str] = "Сообщение от имени бота"


class PlacementTypesDescription(BasePlacementTypes, Enum):
    group_repost: Final[str] = texts["repost_from_group_description"]
    direct_messages_repost: Final[str] = texts["repost_from_user_description"]
    message_from_bot: Final[str] = texts["post_from_bot_description"]


class PlacementTypesMediaPaths(BasePlacementTypes, Enum):
    message_from_bot: Final[str] = "data/media/placement_types/from_bot.jpg"
    group_repost: Final[str] = "data/media/placement_types/from_group.jpg"
    direct_messages_repost: Final[str] = "data/media/placement_types/from_user.jpg"


class PlacementTypesRequirements(BasePlacementTypes, Enum):
    message_from_bot: Final[str] = texts.get("message_from_bot_requirements")
    group_repost: Final[str] = templates.get("reposted_message_requirements").format(
        source=texts.get("from_group_source")
    )
    direct_messages_repost: Final[str] = templates.get("reposted_message_requirements").format(
        source=texts.get("from_user_source")
    )


class PaginationActionTypes(Enum):
    open_next_page: Final[str] = "open_next_page"
    open_previous_page: Final[str] = "open_previous_page"


class AllowedContentTypes(Enum):
    photo: ContentType.PHOTO = ContentType.PHOTO
    video: ContentType.VIDEO = ContentType.VIDEO
    text: ContentType.TEXT = ContentType.TEXT
    document: ContentType.DOCUMENT = ContentType.DOCUMENT

    unknown: ContentType.UNKNOWN = ContentType.UNKNOWN


