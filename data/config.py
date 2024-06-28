from utils.marshalling_tools import Serializer, Deserializer
from dataclasses import dataclass, field
from typing import Final
from os import environ


@dataclass
class RedisJobStoreData:
    HOST: Final[str] = environ.get("REDIS_JOB_STORE_HOST")
    PORT: Final[int] = int(environ.get("REDIS_JOB_STORE_PORT"))
    PASSWORD: Final[str] = environ.get("REDIS_JOB_STORE_PASSWORD")


@dataclass
class Config:
    BOT_TOKEN: Final[str] = environ.get("BOT_TOKEN")
    POSTGRES_ENGINE: Final[str] = environ.get("POSTGRESQL_ENGINE")
    REDIS_URL: Final[str] = environ.get("REDIS_URL")
    REDIS_JOB_STORE_DATA: Final[RedisJobStoreData] = field(default_factory=RedisJobStoreData)
    WEB_APP_URL: Final[str] = environ.get("WEB_APP_URL")


@dataclass
class PricesMetaData:
    """
    This class implements data about prices, which are set by default.
    This class doesn't include price data that come from somewhere else.

    CURRENCY BY DEFAULT: RUB (Rubles)
    """

    ONE_CHAT: Final[int] = 300
    ALL_CHATS: Final[int] = 2000
    ONE_DAY_PIN_FOR_ALL_CHATS: Final[int] = 1500
    ONE_DAY_PIN_FOR_ONE_CHAT: Final[int] = 100


@dataclass
class MetaData:
    CONTACT_US_URL: Final[str] = "https://t.me/n1kol4y"
    MAIN_CHANNEL_URL: Final[str] = "https://t.me/n1kol4y"
    CARD_NUMBER: Final[str] = environ.get("CARD_NUMBER")
    MAX_PIN_DAYS_POSSIBLE: Final[int] = 31


@dataclass
class MenuReferences:

    """
    This class implements saved callbacks which of them are leading to the following menu during the bot usage.
    """

    TO_CHAT_PICK: str = ""
    TO_VARIOUS_CHAT_PICK: str = ""
    TO_PIN_TIME_SELECTION: str = ""
    TO_PLACEMENT_TYPE_SELECTION: str = ""
    TO_WRITE_MESSAGE: str = ""
    TO_CHECK_STAGE: str = ""


@dataclass
class AdminMenuReferences:
    TO_POST_MODERATION: str = ""
    TO_STATISTICS_MENU: str = ""


@dataclass
class ToolBox:
    serializer: Serializer = Serializer()
    deserializer: Deserializer = Deserializer()


config: Final[Config] = Config()
meta: Final[MetaData] = MetaData()
tools: Final[ToolBox] = ToolBox()
price_meta: Final[PricesMetaData] = PricesMetaData()
