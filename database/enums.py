from typing import Final
from enum import Enum


class Roles(Enum):
    user: Final[str] = "user"
    admin: Final[str] = "admin"


class ModerationStatus(Enum):
    approved: Final[str] = "approved"
    waiting: Final[str] = "waiting"
    declined: Final[str] = "declined"
