from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callbacks import BackCallback, PaginationCallback
from aiogram.utils.keyboard import CallbackData
from forms.enums import PaginationActionTypes
from typing import Final, Dict, List, Union
from data.texts import texts
from abc import ABC


class BaseBuilder(InlineKeyboardBuilder, ABC):
    """
    This is a base abstract class that represents main logic and the way inline menus and keyboards are created

    '__name__' must be overridden by inherited class for visual separating in system with '__repr__' method
    """

    __name__ = "BaseBuilder"

    def __repr__(self):
        return f"{self.__name__}Object - ({id(self)})"

    def _init_keyboard(self) -> None:
        """
        This method MUST be called in 'get_keyboard' method in order to provide successful initialization of keyboard.
        Override this method in inherited classes for your purpose in order to create your own keyboard automatically.

        :return: None
        """
        ...

    def get_keyboard(self, back_callback: Union[BackCallback, str] = None) -> InlineKeyboardMarkup:
        """
        This method must include small amount of code, this method is responsible for separating keyboard levels.
        In case if you don't know from which place in your this method will be called, create 'level' variable in your
        inherited class and separate work of your menus on different levels.

        :returns: InlineKeyboardMarkup keyboard based on current level.

        :example:
            def get_keyboard(self) -> InlineKeyboardMarkup:
                if (self.level) == "level":
                    return (your_keyboard)

                else:
                    ...
        """
        ...


class InlineBuilder(BaseBuilder):
    __name__ = "InlineBuilder"
    _BACK_BUTTON_TEXT: str = texts.get("back_button")
    __ONEWAY_MENU_SIGN: Final[str] = "@"
    __BASE_LEVEL: str = "MainMenu"
    __BASE_BACK_BUTTON_CALLBACK: CallbackData = BackCallback(go_to=__BASE_LEVEL)
    _ADJUST_SIZES: List[int] = []
    _LEVEL: str = __BASE_LEVEL

    def __init__(self, level: str = None):
        super().__init__()
        self.back_callback = None
        if level is None:
            self.level: str = self.__BASE_LEVEL

        else:
            self.level: str = level

    @classmethod
    def get_menu_level(cls):
        return cls._LEVEL

    def get_back_button(self, back_callback: Union[BackCallback, str] = None) -> InlineKeyboardButton:
        """
        This method is for adding a 'back' button that leads to previous menu

        :param back_callback: Union[BackCallback, str]
        :return: InlineKeyboardButton
        """

        if back_callback is None:
            return InlineKeyboardButton(
                text="🔙 В главное меню",
                callback_data=self.__BASE_BACK_BUTTON_CALLBACK.pack()
            )
        else:
            if isinstance(back_callback, BackCallback):
                back_callback = back_callback.pack()

            return InlineKeyboardButton(
                text=self._BACK_BUTTON_TEXT,
                callback_data=back_callback
            )

    def get_back_button_keyboard(self, back_callback: Union[BackCallback, str] = None) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[self.get_back_button(back_callback)]])

    def get_keyboard(self, back_callback: Union[BackCallback, str] = None) -> InlineKeyboardMarkup:
        self._markup = list()
        self._init_keyboard()

        if self.__ONEWAY_MENU_SIGN not in self.level:
            if self.level != self.__BASE_LEVEL:
                self.back_callback = back_callback
                self.add(self.get_back_button(back_callback))

        self.adjust(*self._ADJUST_SIZES)
        return self.as_markup()


class FacadeKeyboard(InlineBuilder):
    """
    FacadeKeyboards can be used in different 2 ways.
        -- Dynamic button generation
        -- Static buttons and static callbacks


    How to use static way:
        - Define your menu by overriding '_FACADE' with your buttons by using
        {
            "button_name": "button_callback"
            "button_name2": "button_callback2"
                          ...
            ...e.t.c
        }

    How to use dynamic way:
        - Define your menu by overriding '_init_facade' method, must return Dict with following format:
        {
            "button_name": "button_callback"
            "button_name2": "button_callback2"
                          ...
            ...e.t.c
        }

    """

    __name__ = "FacadeKeyboard"

    __DEFAULT_FACADE: Dict[str, Union[str, CallbackData]] = {
        "button1": "button1_callback",
        "button2": "button2_callback",
        "button3": "button3_callback",
    }

    _FACADE: Dict[str, Union[str, CallbackData]] = __DEFAULT_FACADE

    def __init__(self, level: str = None, data=None):
        super().__init__(level)
        if self._FACADE == self.__DEFAULT_FACADE:
            self._FACADE = self._init_facade(data)

    def _init_facade(self, data=None, **kwargs) -> Dict:
        return kwargs, data

    def _init_keyboard(self) -> None:
        menu_buttons: List[InlineKeyboardButton] = [
            InlineKeyboardButton(text=key, url=value)
            if value.startswith("https://")
            else InlineKeyboardButton(text=key, callback_data=value)
            for key, value in self._FACADE.items()
        ]
        self.add(*menu_buttons)

    def get_facade(self) -> Dict:
        return self._FACADE


class DefaultPageableKeyboard(InlineBuilder):
    
    """
    This class implements functionality of one or more pages with listable items in it.
        
        EXAMPLE: 
              - item 1 -
              - item 2 -
              - item 3 -
              - item 4 -
              - item 5 -
            
        <<   *page_number*   >>  
        
    This is possible with abstract 'Separator'. 
    Firstly you need to create all the buttons and pass them into 'buttons_storage'.
    Then you pass 'max_elements_on_page' (DEFAULT: int = 5) 
    
    """ 
    
    __name__: str = "PageableKeyboard"

    __MIN_PAGE_NUMBER: Final[int] = 1

    def __init__(self, level: str = None, max_elements_on_page: int = 5):
        super().__init__(level=level)
        self._max_elements_on_page: Final[int] = max_elements_on_page
        self._current_page: int = 1
        self._separator: int = 0
        self.buttons_storage: List[InlineKeyboardButton] = []
        self._max_page_count: int = None

    def _count_max_pages(self) -> int:
        buttons_count = len(self.buttons_storage)
        pages_not_round = buttons_count / self._max_elements_on_page
        pages = int(pages_not_round)
        if pages_not_round % 1 != 0:
            pages += 1
        return pages

    def open_next_page(self):
        if self._current_page == self._max_page_count:
            self._current_page = self.__MIN_PAGE_NUMBER
            self._separator = 0
        else:
            self._current_page += 1
            self._separator += self._max_elements_on_page

    def open_previous_page(self):
        if self._current_page == self.__MIN_PAGE_NUMBER:
            self._current_page = self._max_page_count
            self._separator = self._max_elements_on_page
        else:
            self._current_page -= 1
            self._separator -= self._max_elements_on_page

    def _create_page_buttons(self):
        open_previous_page_text = "««"
        current_page_text = str(self._current_page)
        open_next_page_text = "»»"

        open_previous_page_button = InlineKeyboardButton(
            text=open_previous_page_text,
            callback_data=PaginationCallback(action=PaginationActionTypes.open_previous_page).pack()
        )
        current_page_button = InlineKeyboardButton(
            text=current_page_text,
            callback_data=current_page_text
        )
        open_next_page_button = InlineKeyboardButton(
            text=open_next_page_text,
            callback_data=PaginationCallback(action=PaginationActionTypes.open_next_page).pack()
        )

        return [
            open_previous_page_button,
            current_page_button,
            open_next_page_button
        ]

    def get_buttons_to_show(self):
        return self.buttons_storage[self._separator: self._separator + self._max_elements_on_page]


