from .callbacks import ActionCallback
from .base import InlineBuilder, FacadeKeyboard
from aiogram.types import InlineKeyboardButton
from data.config import config, meta
from typing import Final, List, Dict

CONTACT_ME_URL: Final[str] = "https://t.me/Meorwik"


class MainMenuBuilder(InlineBuilder):
    __name__ = "MainMenuBuilder"

    _ADJUST_SIZES: List[int] = [1]

    _ACTIONS: Final[Dict[str, str]] = {
        "place_advertisement": "Разместить рекламу",
        "services_price": "Стоимость услуг",
        "open_channel": "Перейти в канал",
        "contact_us": "Сотрудничество"
    }

    def _init_keyboard(self) -> None:
        menu_buttons: List[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=self._ACTIONS.get("place_advertisement"),
                callback_data=ActionCallback(
                    menu_level=self.level,
                    action="place_advertisement"
                ).pack()
            ),
            InlineKeyboardButton(
                text=self._ACTIONS.get("services_price"),
                callback_data=ActionCallback(
                    menu_level=self.level,
                    action="services_price"
                ).pack()
            ),
            InlineKeyboardButton(text=self._ACTIONS.get("open_channel"), url=meta.MAIN_CHANNEL_URL),
            InlineKeyboardButton(text=self._ACTIONS.get("contact_us"), url=meta.CONTACT_US_URL)
        ]
        self.add(*menu_buttons)

