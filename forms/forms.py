from typing import List, Union, Dict
from dataclasses import dataclass, field
from .enums import PlacementTypes
from database.models import ChatGroup


class Form:
    def as_dict(self) -> Dict:
        return self.__dict__


class MessageToPlaceForm(Form):
    text: str
    # TODO: write the rest of the MessageToPlace form including the way how to store different media


@dataclass
class ElectiveChatGroup(Form):
    chats: List[Union[str, int]] = field(default_factory=list)


@dataclass
class PlaceAdvertisementForm(Form):
    chats: List[Union[str, int, ChatGroup, ElectiveChatGroup]] = field(default_factory=list)
    placement_type: PlacementTypes = None
    message: MessageToPlaceForm = field(default_factory=MessageToPlaceForm)
    pin_days: int = 0
    total_cost: int = 0
