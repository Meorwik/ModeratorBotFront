from .callbacks import ActionCallback, AdminCallback, BackCallback, DataPassCallback
from .base import FacadeKeyboard, DefaultPageableKeyboard, InlineBuilder
from .keyboards import PinTimeSelectionBuilder
from aiogram.types import InlineKeyboardButton
from datetime import datetime, timedelta
from typing import Final, List, Dict
from forms.forms import DecodedPost
import calendar


class AdminMainMenuKeyboard(FacadeKeyboard):
    _ADJUST_SIZES = [1]

    def __init__(self):
        super().__init__()

    def _init_facade(self, data=None, **kwargs) -> Dict:
        facade: Final[Dict] = {
            "Статистика": AdminCallback(menu_level=self.level, action="statistics").pack(),
            "Размещения": AdminCallback(menu_level=self.level, action="placements").pack(),
            "Начать модерацию": AdminCallback(menu_level=self.level, action="start_moderation").pack()
        }
        return facade


class AdminModerationKeyboard(FacadeKeyboard):

    _LEVEL = "ModerationKeyboard"

    _FACADE = {
        "Одобрить": AdminCallback(menu_level=_LEVEL, action="approved").pack(),
        "Нужно внести правки": AdminCallback(menu_level=_LEVEL, action="make_notes").pack()
    }

    _ADJUST_SIZES = [1]

    def __init__(self):
        super().__init__(level=self._LEVEL)


class DeclinedPostKeyboard(FacadeKeyboard):
    _LEVEL: str = "@DeclinedPostKeyboard"

    _ADJUST_SIZES: List[int] = [1]

    _FACADE = {
        "Внести правки": ActionCallback(menu_level=_LEVEL, action=f"edit_post").pack(),
        "Отменить публикацию": ActionCallback(menu_level=_LEVEL, action="cancel_post").pack()
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class ContinueModerationKeyboard(FacadeKeyboard):
    _LEVEL: str = "@ContinueModerationKeyboard"

    _ADJUST_SIZES: List[int] = [1]

    _FACADE = {
        "Продолжить ➡️": AdminCallback(menu_level=_LEVEL, action="continue").pack(),
        "Завершить ❗️": BackCallback(go_to="AdminMainMenu").pack()
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class StatisticsKeyboard(FacadeKeyboard):
    _LEVEL = "StatisticsKeyboard"

    _ADJUST_SIZES: List[int] = [1]

    _FACADE = {
        "Оборот 💸": AdminCallback(menu_level=_LEVEL, action="income").pack(),
        "Публикации 📝": AdminCallback(menu_level=_LEVEL, action="posts").pack(),
        "Пользователи 👤": AdminCallback(menu_level=_LEVEL, action="users").pack()
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class AcceptPaymentKeyboard(FacadeKeyboard):
    _LEVEL = "@AcceptPayment"

    _ADJUST_SIZES: List[int] = [1]

    def __init__(self, request_id: int):
        super().__init__(level=self._LEVEL, data=request_id)

    def _init_facade(self, data=None, **kwargs) -> Dict:
        request_id: str = str(data)

        facade: Dict = {
            "Получил оплату ✅": DataPassCallback(
                menu_level=self.level,
                action=f"successful_payment",
                data=request_id
            ).pack(),

            "Не получил ❌": DataPassCallback(
                menu_level=self.level,
                action=f"failed_payment",
                data=request_id
            ).pack(),
        }
        return facade


class CalendarKeyboard(FacadeKeyboard):

    _LEVEL = "CalendarKeyboard"

    _ADJUST_SIZES = [3, 5, 5, 5, 5, 5, 5, 1]

    __FIRST_DAY_OF_MONTH: Final[int] = 1
    __LAST_DAY_OF_MONTH_INDEX: Final[int] = 1
    __THRESHOLD_DAYS_REMAINING: Final[int] = 5

    def _init_facade(self, data=None, **kwargs) -> Dict:
        year: int = data[0]
        month: int = data[1]
        post_schedule: List[str] = data[2]

        days_facade: Dict = {}

        month_days = calendar.monthrange(year, month)[self.__LAST_DAY_OF_MONTH_INDEX]
        today = datetime.today()
        current_day = today.day if today.year == year and today.month == month else None

        if current_day and (month_days - current_day < self.__THRESHOLD_DAYS_REMAINING):
            month += 1
            if month > 12:
                month = 1
                year += 1
            month_days = calendar.monthrange(year, month)[self.__LAST_DAY_OF_MONTH_INDEX]
            current_day = None

        days_facade.update(
            {
                "⬅️": DataPassCallback(menu_level=self.level, action="prev", data=f"{year}_{month}").pack(),
                f"{calendar.month_name[month]} {year}": DataPassCallback(
                    menu_level=self.level, action="ignore", data="None"
                ).pack(),
                "➡️": DataPassCallback(menu_level=self.level, action="next", data=f"{year}_{month}").pack(),
            }
        )

        for day in range(1, month_days + 1):
            day_text = f'{day} 🟢' if day == current_day else str(day)
            day_text = f'📋{day_text}' if str(day) in post_schedule else day_text
            days_facade[day_text] = DataPassCallback(
                menu_level=self.level,
                action="date",
                data=f"{year}-{month}-{day}"
            ).pack()

        return days_facade

    def __init__(self,  year: int, month: int, post_schedule: List[str]):
        super().__init__(level=self._LEVEL, data=(year, month, post_schedule))


class PostSelectionKeyboard(DefaultPageableKeyboard):

    _ADJUST_SIZES: List[int] = [1, 1, 1, 1, 1, 1, 1, 3]

    _LEVEL = "PostSelection"
    __MAX_ELEMENTS_ON_PAGE: Final[int] = 5
    __POST_NAME_LENGTH: Final[int] = 20

    def __init__(self, posts: List[DecodedPost]):
        super().__init__(level=self._LEVEL, max_elements_on_page=self.__MAX_ELEMENTS_ON_PAGE)
        self.__posts: List[DecodedPost] = posts
        self.buttons_storage: List[InlineKeyboardButton] = self.__create_post_buttons()
        self._max_page_count: Final[int] = self._count_max_pages()

    def __create_post_buttons(self) -> List[InlineKeyboardButton]:
        buttons: List[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=post.post.message.text[:self.__POST_NAME_LENGTH],
                callback_data=DataPassCallback(menu_level=self._LEVEL, action=f"post", data=f"{post.id}").pack()
            )
            for post in self.__posts
        ]
        return buttons

    def _init_keyboard(self) -> None:
        if len(self.buttons_storage) == 0:
            self.add(
                InlineKeyboardButton(text="На эту дату нет размещений", callback_data="ignore")
            )

        else:
            buttons_to_show: List[InlineKeyboardButton] = self.get_buttons_to_show()

            if len(self.buttons_storage) > self.__MAX_ELEMENTS_ON_PAGE:
                self._ADJUST_SIZES: List[int] = [*([1] * len(buttons_to_show)), 3]
                self.add(*buttons_to_show)
                self.row(*self._create_page_buttons())

            else:
                self.add(*buttons_to_show)


class PostInteractionKeyboard(FacadeKeyboard):

    _ADJUST_SIZES: List[int] = [1]

    _LEVEL = "PostInteraction"

    def __init__(self, is_forward: bool):
        super().__init__(level=self._LEVEL, data=is_forward)

    def _init_facade(self, data=None, **kwargs) -> Dict:
        is_forward: bool = data
        facade: Dict = {}

        if not is_forward:
            facade["Изменить"] = AdminCallback(menu_level=self.level, action="modify").pack()

        facade["Отменить"] = AdminCallback(menu_level=self.level, action="cancel_post").pack()

        return facade


class PostCancellationConfirmKeyboard(FacadeKeyboard):

    _ADJUST_SIZES: List[int] = [1]

    _LEVEL = "PostCancellationConfirm"

    _FACADE = {
        "Да, я хочу отменить": AdminCallback(menu_level=_LEVEL, action="cancel").pack()
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class PostModifyKeyboard(FacadeKeyboard):

    _ADJUST_SIZES = [1]
    _LEVEL = "PostModifyKeyboard"

    def __init__(self, has_media: bool = None, is_document: bool = None):
        super().__init__(level=self._LEVEL, data=(has_media, is_document))

    def _init_facade(self, data=None, **kwargs) -> Dict:
        has_media: bool = data[0]
        is_document: bool = data[1]

        facade: Dict = {
            "📌⚙️ Настройки закрепления": AdminCallback(menu_level=self._LEVEL, action="pin_modify").pack()
        }

        if not is_document:
            facade["📎 Прикрепить медиа"] = AdminCallback(menu_level=self._LEVEL, action="attach_media").pack()

        if has_media:
            facade["🗑🖼 Удалить все медиа"] = AdminCallback(menu_level=self._LEVEL, action="delete_all_media").pack()

        facade["✅ Продолжить"] = AdminCallback(menu_level=self._LEVEL, action="complete").pack()

        return facade


class AdminPinTimeSelectionBuilder(PinTimeSelectionBuilder):

    _LEVEL = "PinTimeSelectionBuilder"

    _FACADE: Dict = {
        "Без закрепления": AdminCallback(menu_level=_LEVEL, action="0").pack(),
        "Закреп на 1 сутки": AdminCallback(menu_level=_LEVEL, action="1").pack(),
        "Закреп на 2 суток": AdminCallback(menu_level=_LEVEL, action="2").pack(),
        "Закреп на 5 суток": AdminCallback(menu_level=_LEVEL, action="5").pack(),
        "Указать количество дней": AdminCallback(menu_level=_LEVEL, action="write_days_count").pack(),
    }

    def __init__(self):
        super().__init__()

