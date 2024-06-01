from .callbacks import ActionCallback
from .base import InlineBuilder, FacadeKeyboard, PageableKeyboard
from aiogram.types import InlineKeyboardButton, WebAppInfo
from database.models import Chat, ChatGroup
from data.config import config, meta
from typing import Final, List, Dict, Union, Set

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


class ChatSelectionBuilder(InlineBuilder):
    __name__ = "ChatSelectionBuilder"

    _ADJUST_SIZES: List[int] = [2, 2, 2, 2, 2, 1]
    _LEVEL = "ChatSelection"

    def __init__(self, chat_groups: List[ChatGroup]):
        super().__init__(level=self._LEVEL)
        self.chat_groups: List[ChatGroup] = chat_groups

    def _init_keyboard(self) -> List[InlineKeyboardButton]:
        chat_selection_buttons: List[InlineKeyboardButton] = []

        for chat in self.chat_groups:
            chat_selection_buttons.append(InlineKeyboardButton(
                text=chat.name, callback_data=ActionCallback(
                    menu_level=self._LEVEL,
                    action=f"{chat.id}").pack()
                )
            )
            chat_selection_buttons.append(InlineKeyboardButton(text="Просмотр чата", url="https://www.google.com"))

        select_various_chats: InlineKeyboardButton = InlineKeyboardButton(
            text="Выбрать несколько чатов",
            callback_data=ActionCallback(menu_level=self._LEVEL, action="select_various_chats").pack()
        )

        select_all: InlineKeyboardButton = InlineKeyboardButton(
            text="Весь город",
            callback_data=ActionCallback(menu_level=self._LEVEL, action="select_all").pack()
        )

        chat_selection_buttons.append(select_various_chats)
        chat_selection_buttons.append(select_all)

        self.add(*chat_selection_buttons)


class VariousChatSelectionBuilder(PageableKeyboard):
    __name__ = "VariousChatSelectionBuilder"

    _ADJUST_SIZES: List[int] = [1, 1, 1, 1, 1, 1, 1, 3]
    _LEVEL = "VariousChatSelection"

    _ACTIONS: Final[Dict[str, str]] = {
        "all_chats": "Все чаты",
        "submit": "Подтвердить",
    }

    __SELECT_EMOJI: Final[str] = "✔️ "
    __OPTIONS_BUTTON_COUNT: Final[int] = 5
    __ALL_CHATS_BUTTON_INDEX: Final[int] = -2
    __MAX_ELEMENTS_ON_PAGE: Final[int] = 5

    def __init__(self, chats: List[Chat]):
        super().__init__(level=self._LEVEL, max_elements_on_page=self.__MAX_ELEMENTS_ON_PAGE)
        self.__chats: List[Chat] = chats
        self.buttons_storage: List[InlineKeyboardButton] = self.__create_chat_buttons()
        self._max_page_count: Final[int] = self._count_max_pages()
        self.__marked_chats: Set[Union[str, int]] = set()

    @property
    def selected_chats(self) -> Set[str]:
        return self.__marked_chats

    @selected_chats.setter
    def selected_chats(self, value: Set[str]):
        self.__marked_chats = value

    def __get_keyboard_copy(self) -> List[List[InlineKeyboardButton]]:
        return self.as_markup().inline_keyboard.copy()

    def __mark(self, button: InlineKeyboardButton) -> InlineKeyboardButton:
        if not self.__is_marked(button):
            button.text = f"{self.__SELECT_EMOJI}" + button.text

    def __unmark(self, button: InlineKeyboardButton):
        if self.__is_marked(button):
            button.text = button.text.removeprefix(self.__SELECT_EMOJI)

    def __is_marked(self, button: InlineKeyboardButton) -> bool:
        return self.__SELECT_EMOJI in button.text

    def __get_chat_id(self, button: InlineKeyboardButton) -> str:
        return ActionCallback.unpack(button.callback_data).action

    def __refresh_keyboard(self):
        for button in self.buttons_storage:
            is_marked: bool = self.__is_marked(button)
            chat_id: str = self.__get_chat_id(button)

            if chat_id in self.__marked_chats and not is_marked:
                self.__mark(button)

            elif chat_id not in self.__marked_chats and is_marked:
                self.__unmark(button)

    def __create_option_buttons(self) -> List[InlineKeyboardButton]:
        buttons: Final[List[InlineKeyboardButton]] = []

        all_chats_button: Final[InlineKeyboardButton] = InlineKeyboardButton(
            text=self._ACTIONS["all_chats"],
            callback_data=ActionCallback(menu_level=self._LEVEL, action="all_chats").pack()
        )
        submit_button: Final[InlineKeyboardButton] = InlineKeyboardButton(
            text=self._ACTIONS["submit"],
            callback_data=ActionCallback(menu_level=self._LEVEL, action="submit").pack()
        )
        buttons.append(all_chats_button)
        buttons.append(submit_button)
        return buttons

    def __create_chat_buttons(self) -> List[InlineKeyboardButton]:
        buttons: List[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=chat.chat_name,
                callback_data=ActionCallback(menu_level=self._LEVEL, action=f"{chat.chat_id}").pack()
            )
            for chat in self.__chats
        ]
        return buttons

    def __mark_all_as_selected(self):
        for button in self.buttons_storage:
            self.__mark(button)

    def __unmark_all_as_selected(self):
        for button in self.buttons_storage:
            self.__unmark(button)

    def _init_keyboard(self) -> None:
        self.__refresh_keyboard()
        buttons_to_show: List[InlineKeyboardButton] = self.get_buttons_to_show()
        self._ADJUST_SIZES: List[int] = [*([1] * (len(buttons_to_show) + 2)), 3]
        self.add(*buttons_to_show)
        self.add(*self.__create_option_buttons())
        self.row(*self._create_page_buttons())

    def mark_all_as_selected(self, chat_ids: Set[Union[str, int]]):
        chat_ids: Set[str] = set([str(chat_id) for chat_id in chat_ids])
        self.__marked_chats = chat_ids

    def unmark_all_as_selected(self):
        self.__marked_chats.clear()

    def mark_as_selected(self, chat_id: Union[str, int]):
        self.__marked_chats.add(chat_id)

    def unmark_as_selected(self, chat_id: Union[str, int]):
        self.__marked_chats.remove(chat_id)


class PinTimeSelectionBuilder(FacadeKeyboard):
    __name__: str = "PinTimeSelectionBuilder"

    _LEVEL = "PinTimeSelection"
    _ADJUST_SIZES = [1]

    _FACADE: Dict = {
        "Без закрепления": ActionCallback(menu_level=_LEVEL, action="0").pack(),
        "Закреп на 1 сутки": ActionCallback(menu_level=_LEVEL, action="1").pack(),
        "Закреп на 2 суток": ActionCallback(menu_level=_LEVEL, action="2").pack(),
        "Закреп на 5 суток": ActionCallback(menu_level=_LEVEL, action="5").pack(),
        "Указать количество дней": ActionCallback(menu_level=_LEVEL, action="write_days_count").pack(),
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class PlacementTypeSelection(FacadeKeyboard):
    __name__: str = "PlacementTypeSelection"

    _LEVEL = "PlacementTypeSelection"
    _ADJUST_SIZES = [3, 1, 1]

    _FACADE: Dict = {
        "⬅️": ActionCallback(menu_level=_LEVEL, action="previous_option").pack(),
        "Выбрать": ActionCallback(menu_level=_LEVEL, action="select_option").pack(),
        "➡️": ActionCallback(menu_level=_LEVEL, action="next_option").pack(),
    }

    __MAX_OPTIONS_COUNT: Final[int] = 3
    __SELECT_BUTTON_INDEX: Final[int] = 1

    def __init__(self):
        super().__init__(level=self._LEVEL)
        self.__option_number = 1

    def __create_additional_buttons(self) -> List[InlineKeyboardButton]:
        choose_datetime_button: InlineKeyboardButton = InlineKeyboardButton(
            text="Выбрать дату и время",
            web_app=WebAppInfo(url=config.WEB_APP_URL),
        )
        send_message_button: InlineKeyboardButton = InlineKeyboardButton(
            text="Отправить сообщение",
            callback_data=ActionCallback(menu_level=self.level, action="send_message").pack()
        )
        return [choose_datetime_button, send_message_button]

    def _init_keyboard(self) -> None:
        buttons: List[InlineKeyboardButton] = []
        for text, callback in self._FACADE.items():
            buttons.append(
                InlineKeyboardButton(text=text, callback_data=callback)
            )

        for button in self.__create_additional_buttons():
            buttons.append(button)

        self.add(*buttons)

    def next_option(self):
        self.__option_number += 1

    def previous_option(self):
        self.__option_number -= 1

    def is_marked(self) -> bool:
        button: InlineKeyboardButton = self.as_markup().inline_keyboard[0][self.__SELECT_BUTTON_INDEX]
        return "✅" in button.text

    def mark_option(self):
        button: InlineKeyboardButton = self.as_markup().inline_keyboard[0][self.__SELECT_BUTTON_INDEX]
        button.text = "✅ Выбранно"

    def unmark_option(self):
        button: InlineKeyboardButton = self.as_markup().inline_keyboard[0][self.__SELECT_BUTTON_INDEX]
        button.text = "Выбрать"

    @property
    def option_number(self):
        return self.__option_number

    @option_number.setter
    def option_number(self, value):
        if self.__option_number + value > self.__MAX_OPTIONS_COUNT:
            raise ValueError
        else:
            self.__option_number += value
