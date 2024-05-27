from aiogram.utils.keyboard import CallbackData
from forms.enums import PaginationActionTypes
from typing import Final, Union

"""
                            ~~PREFIXES~~
"""

BACK_CALLBACK_PREFIX: Final[str] = "BACK_TO"
ACTION_CALLBACK_PREFIX: Final[str] = "DO_ACTION"
PAGINATION_CALLBACK_PREFIX: Final[str] = "PAGE_TO"


class ActionCallback(CallbackData, prefix=ACTION_CALLBACK_PREFIX):
    menu_level: str
    action: str


class BackCallback(CallbackData, prefix=BACK_CALLBACK_PREFIX):
    go_to: str


class PaginationCallback(CallbackData, prefix=PAGINATION_CALLBACK_PREFIX):
    action: PaginationActionTypes



