from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import WebAppInfo
from typing import Final, List
from data.config import config
from data.texts import texts


class WebAppKeyboard(ReplyKeyboardBuilder):

    ADJUST_SIZES: Final[List[int]] = [1]

    def __init__(self):
        super().__init__()
        self.__web_app_url: str = config.WEB_APP_URL

    def get_keyboard(self) -> ReplyKeyboardMarkup:
        web_app_button: KeyboardButton = KeyboardButton(
            text="Выбрать дату и время ⏳",
            web_app=WebAppInfo(url=self.__web_app_url)
        )
        go_back_button: KeyboardButton = KeyboardButton(
            text=texts.get("back_button")
        )

        self.add(web_app_button)
        self.add(go_back_button)
        self.adjust(*self.ADJUST_SIZES)

        return self.as_markup(resize_keyboard=True)

    def get_keyboard_webapp_only(self):
        web_app_button: KeyboardButton = KeyboardButton(
            text="Выбрать дату и время ⏳",
            web_app=WebAppInfo(url=self.__web_app_url)
        )

        self.add(web_app_button)
        self.adjust(*self.ADJUST_SIZES)

        return self.as_markup(resize_keyboard=True)

