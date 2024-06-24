from .admins_handler import admin_router
from aiogram import Router
from typing import Final

admin_router_main: Final[Router] = Router(name="commands")
admin_router_main.include_router(admin_router)

