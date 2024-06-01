from utils.marshalling_tools import Serializer, Deserializer
from dataclasses import dataclass
from typing import Final
from os import environ


@dataclass
class Config:
    BOT_TOKEN: Final[str] = environ.get("BOT_TOKEN")
    POSTGRES_ENGINE: Final[str] = environ.get("POSTGRESQL_ENGINE")
    REDIS_URL: Final[str] = environ.get("REDIS_URL")
    WEB_APP_URL: Final[str] = environ.get("WEB_APP_URL")


@dataclass
class PricesMetaData:
    """
    This class implements data about prices, which are set by default.
    This class doesn't include price data that come from somewhere else.

    CURRENCY BY DEFAULT: RUB (Rubles)
    """

    ONE_CHAT: Final[int] = 300
    ONE_DAY_PIN_FOR_ALL_CHATS: Final[int] = 1500
    ONE_DAY_PIN_FOR_ONE_CHAT: Final[int] = 100


@dataclass
class MetaData:
    CONTACT_US_URL: Final[str] = "https://t.me/Meorwik"
    MAIN_CHANNEL_URL: Final[str] = "https://t.me/Meorwik"
    MAX_PIN_DAYS_POSSIBLE: Final[int] = 31


@dataclass
class MenuReferences:

    """
    This class implements saved callbacks which of them are leading to the following menu during the bot usage.
    """

    TO_CHAT_PICK: str = ""
    TO_VARIOUS_CHAT_PICK: str = ""
    TO_PIN_TIME_SELECTION: str = ""


@dataclass
class ToolBox:
    serializer: Serializer = Serializer()
    deserializer: Deserializer = Deserializer()


config: Final[Config] = Config()
meta: Final[MetaData] = MetaData()
tools: Final[ToolBox] = ToolBox()
