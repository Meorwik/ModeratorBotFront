from .place_advertisement_handler import place_advertisement_menu_router
from .moderation_feedback_handler import moderation_feedback_router
from .paginator_handler import paginator_router
from .main_menu import main_menu_router
from aiogram import Router
from typing import Final

menus_router: Final[Router] = Router(name="menus")
menus_router.include_router(main_menu_router)
menus_router.include_router(place_advertisement_menu_router)
menus_router.include_router(paginator_router)
menus_router.include_router(moderation_feedback_router)
