from dataclasses import dataclass, field
from database.enums import PostStatus
from database.models import ChatGroup
from .enums import PlacementTypes
from aiogram.types import Message
from datetime import datetime
from typing import List, Union
from .base import Form


@dataclass
class UserForm(Form):
    id: Union[str, int] = None
    username: str = None


@dataclass
class MessageToPlaceForm(Form):
    text: str = None
    only_text: bool = None

    album: List[Message] = field(default_factory=list)

    is_forward: bool = None
    message_id: int = None
    from_user: UserForm = None

    is_document: bool = None
    document: str = None


@dataclass
class ElectiveChatGroup(Form):
    chats: List[Union[str, int]] = field(default_factory=list)
    all_city: bool = False


@dataclass
class PlaceAdvertisementForm(Form):
    chats: Union[ChatGroup, ElectiveChatGroup] = field(default_factory=list)
    placement_type: PlacementTypes = None
    message: MessageToPlaceForm = field(default_factory=MessageToPlaceForm)
    pin_days: int = 0
    time: str = None
    date: str = None
    total_cost: int = 0


@dataclass
class ModeratedAdvertisementForm(Form):
    request_id: int
    advertisement_form: PlaceAdvertisementForm


@dataclass
class DecodedPost(Form):
    id: int
    job_id: str
    status: PostStatus
    publish_date: datetime
    post: PlaceAdvertisementForm
    chats: List[int]
    message_ids: List[int]
