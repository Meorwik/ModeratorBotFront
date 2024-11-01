from .base import InlineBuilder, FacadeKeyboard, DefaultPageableKeyboard
from typing import Final, List, Dict, Union, Set
from aiogram.types import InlineKeyboardButton
from database.models import Chat, ChatGroup
from forms.enums import PlacementTypes
from .callbacks import ActionCallback, DataPassCallback
from data.config import config, meta


class MainMenuBuilder(InlineBuilder):
    __name__ = "MainMenuBuilder"

    _ADJUST_SIZES: List[int] = [1]

    _ACTIONS: Final[Dict[str, str]] = {
        "place_advertisement": "Разместить информацию в чатах",
        "services_price": "Узнать стоимость размещения",
        "open_channel": "Можете перейти в наш канал",
        "contact_us": "Связаться с администратором"
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


class ChatGroupSelectionBuilder(InlineBuilder):
    __name__ = "ChatSelectionBuilder"

    _ADJUST_SIZES: List[int] = [1]
    _LEVEL = "ChatSelection"

    def __init__(self, chat_groups: List[ChatGroup]):
        super().__init__(level=self._LEVEL)
        self.chat_groups: List[ChatGroup] = chat_groups

    def _init_keyboard(self):
        chat_selection_buttons: List[InlineKeyboardButton] = []

        for chat in self.chat_groups:
            chat_selection_buttons.append(InlineKeyboardButton(
                text=chat.name, callback_data=ActionCallback(
                    menu_level=self._LEVEL,
                    action=f"{chat.id}").pack()
                )
            )

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


class VariousChatSelectionBuilder(DefaultPageableKeyboard):
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

    def __mark(self, button: InlineKeyboardButton):
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

    def mark_all_as_selected(self, chat_ids: List[Union[str, int]]):
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
        "Публикация без закрепления": ActionCallback(menu_level=_LEVEL, action="0").pack(),
        "Закрепление на 1 сутки": ActionCallback(menu_level=_LEVEL, action="1").pack(),
        "Закрепление на 2 суток": ActionCallback(menu_level=_LEVEL, action="2").pack(),
        "Закрепление на 5 суток": ActionCallback(menu_level=_LEVEL, action="5").pack(),
        "Иное количество дней с закреплением": ActionCallback(menu_level=_LEVEL, action="write_days_count").pack(),
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class PlacementTypeSelection(FacadeKeyboard):
    __name__: str = "PlacementTypeSelection"

    _LEVEL = "PlacementTypeSelection"
    _ADJUST_SIZES = [3, 1]

    _FACADE: Dict = {
        "⬅️": ActionCallback(menu_level=_LEVEL, action="previous_option").pack(),
        "Выбрать": ActionCallback(menu_level=_LEVEL, action="select_option").pack(),
        "➡️": ActionCallback(menu_level=_LEVEL, action="next_option").pack(),
        "Отправить сообщение": ActionCallback(menu_level=_LEVEL, action="send_message").pack()
    }

    __MAX_OPTIONS_COUNT: Final[int] = 2
    __MIN_OPTIONS_COUNT: Final[int] = 1
    __SELECT_BUTTON_INDEX: Final[int] = 1

    def __init__(self):
        super().__init__(level=self._LEVEL)
        self.__option_number = 1
        self.buttons_storage: List[InlineKeyboardButton] = self.__create_buttons()

    def __create_buttons(self) -> List[InlineKeyboardButton]:
        buttons: List[InlineKeyboardButton] = []
        for text, callback in self._FACADE.items():
            buttons.append(
                InlineKeyboardButton(text=text, callback_data=callback)
            )

        return buttons

    def _init_keyboard(self) -> None:
        self.add(*self.buttons_storage)

    def next_option(self):
        if self.__option_number == self.__MAX_OPTIONS_COUNT:
            self.__option_number = self.__MIN_OPTIONS_COUNT
        else:
            self.__option_number += 1

    def previous_option(self):
        if self.__option_number == self.__MIN_OPTIONS_COUNT:
            self.__option_number = self.__MAX_OPTIONS_COUNT
        else:
            self.__option_number -= 1

    def is_marked(self) -> bool:
        select_button: InlineKeyboardButton = self.buttons_storage[self.__SELECT_BUTTON_INDEX]
        return "✅" in select_button.text

    def mark_option(self):
        select_button: InlineKeyboardButton = self.buttons_storage[self.__SELECT_BUTTON_INDEX]
        select_button.text = "✅ Выбранно"

    def unmark_option(self):
        select_button: InlineKeyboardButton = self.buttons_storage[self.__SELECT_BUTTON_INDEX]
        select_button.text = "Выбрать"

    @property
    def option_number(self):
        return self.__option_number


class CompletePlaceAdvertisementFormMenu(FacadeKeyboard):
    __name__: str = "CompletePlaceAdvertisementFormBuilder"

    _ADJUST_SIZES = [1]
    _LEVEL = "CompletePlaceAdvertisementForm"

    def __init__(self, placement_type: PlacementTypes, has_media: bool = None, is_document: bool = None):
        super().__init__(level=self._LEVEL, data=(placement_type, has_media, is_document))

    def _init_facade(self, data=None, **kwargs) -> Dict:
        placement_type: PlacementTypes = data[0]
        has_media: bool = data[1]
        is_document: bool = data[2]

        if placement_type == PlacementTypes.message_from_bot:
            facade: Dict = {"✏️ Изменить": ActionCallback(menu_level=self._LEVEL, action="modify").pack()}

            if not is_document:
                facade["📎 Прикрепить медиа"] = ActionCallback(menu_level=self._LEVEL, action="attach_media").pack()

            facade["✅ Продолжить"] = ActionCallback(menu_level=self._LEVEL, action="complete").pack()

            if has_media:
                facade["Удалить все медиа"] = ActionCallback(menu_level=self._LEVEL, action="delete_all_media").pack()

        else:
            facade: Dict = {
                "✅ Продолжить": ActionCallback(menu_level=self._LEVEL, action="complete").pack(),
            }

        return facade


class SelectPaymentMethodKeyboard(FacadeKeyboard):

    _ADJUST_SIZES = [1]
    _LEVEL = "@SelectPaymentMethodKeyboard"

    def __init__(self, advertisement_form: str):
        super().__init__(level=self._LEVEL, data=advertisement_form)

    def _init_facade(self, data=None, **kwargs) -> Dict:
        advertisement_form: str = str(data)

        facade: Dict = {
            "Оплатить": DataPassCallback(
                menu_level=self.level,
                action="individual",
                data=advertisement_form
            ).pack(),

            "Отменить публикацию": DataPassCallback(
                menu_level=self.level,
                action="cancel_request",
                data=advertisement_form
            ).pack(),
        }

        return facade


class PaymentProviderKeyboard(FacadeKeyboard):

    _ADJUST_SIZES = [1]
    _LEVEL = "@PaymentProviderKeyboard"

    def __init__(self, is_entity: bool, advertisement_form):
        super().__init__(level=self._LEVEL, data=(is_entity, advertisement_form))

    def _init_facade(self, data=None, **kwargs) -> Dict:
        advertisement_form = data[1]

        facade: Dict = {
            "Оплатил": ActionCallback(menu_level=self.level, action="paid").pack(),

            "Отменить публикацию": DataPassCallback(
                menu_level="@SelectPaymentMethodKeyboard",
                action="cancel_request",
                data=advertisement_form
            ).pack(),

            "Назад":  ActionCallback(
                menu_level=self.level,
                action="to_successfully_moderated_msg",
            ).pack()
        }

        return facade


class PaymentCheckResultKeyboard(FacadeKeyboard):

    _ADJUST_SIZES = [1]
    _LEVEL = "@PaymentCheckResultKeyboard"

    def __init__(self, is_paid: bool):
        super().__init__(level=self._LEVEL, data=is_paid)

    def _init_facade(self, data=None, **kwargs) -> Dict:
        is_paid: bool = data

        if is_paid:
            facade: Dict = {
                "✅ Подтверждаю": ActionCallback(menu_level=self.level, action="confirm").pack(),
            }

        else:
            facade: Dict = {
                "Связаться с админом 👤": meta.CONTACT_US_URL,
                "Подтвердить оплату повторно": ActionCallback(menu_level="@PaymentProviderKeyboard", action="paid").pack(),
                "Вернуться в начало": ActionCallback(menu_level=self.level, action="restart").pack()
            }

        return facade

class FinalKeyboard(FacadeKeyboard):
    _ADJUST_SIZES = [1]
    _LEVEL = "@FinalKeyboard"

    def __init__(self):
        super().__init__(level=self._LEVEL)

    def _init_facade(self, data=None, **kwargs) -> Dict:
        facade: Dict = {
            "Вернуться в начало": ActionCallback(menu_level="@PaymentCheckResultKeyboard", action="restart").pack()
        }

        return facade