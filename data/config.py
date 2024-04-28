from dataclasses import dataclass
from typing import Final
from os import environ


@dataclass
class Config:
    BOT_TOKEN: Final[str] = environ.get("BOT_TOKEN")


@dataclass
class MetaData:
    CONTACT_US_URL: Final[str] = "https://t.me/Meorwik"
    MAIN_CHANNEL_URL: Final[str] = "https://t.me/Meorwik"


@dataclass
class FormPostConstants:
    main_menu_stage: Final[str] = "main_menu"
    pick_chats_stage: Final[str] = "pick_chats"


config: Final[Config] = Config()
meta: Final[MetaData] = MetaData()
