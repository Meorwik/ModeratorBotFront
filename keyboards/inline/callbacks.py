from aiogram.utils.keyboard import CallbackData
from typing import Final, Union

"""
                            ~~PREFIXES~~
"""

BACK_CALLBACK_PREFIX: Final[str] = "BACK_TO"
ACTION_CALLBACK_PREFIX: Final[str] = "DO_ACTION"


class ActionCallback(CallbackData, prefix=ACTION_CALLBACK_PREFIX):
    menu_level: str
    action: str


class BackCallback(CallbackData, prefix=BACK_CALLBACK_PREFIX):
    go_to: str



