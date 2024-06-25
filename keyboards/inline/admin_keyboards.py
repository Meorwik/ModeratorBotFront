from .base import InlineBuilder, FacadeKeyboard, PageableKeyboard
from .callbacks import ActionCallback, AdminCallback, BackCallback
from typing import Final, List, Dict, Union, Set
from aiogram.types import InlineKeyboardButton
from database.models import Chat, ChatGroup
from forms.enums import PlacementTypes
from data.config import config, meta


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
    _LEVEL: str = "DeclinedPostKeyboard"

    _ADJUST_SIZES: List[int] = [1]

    _FACADE = {
        "Внести правки": ActionCallback(menu_level=_LEVEL, action=f"edit_post").pack(),
        "Отменить публикацию": ActionCallback(menu_level=_LEVEL, action="cancel_post").pack()
    }

    def __init__(self):
        super().__init__(level=self._LEVEL)


class ContinueModerationKeyboard(FacadeKeyboard):
    _LEVEL: str = "ContinueModerationKeyboard"

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


