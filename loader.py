from aiogram.fsm.storage.redis import RedisStorage
from database.postgresql import PostgresManager
from aiogram.enums.parse_mode import ParseMode
from aiogram import Bot, Dispatcher, Router
from data.config import config
from typing import Final

postgres: Final[PostgresManager] = PostgresManager(engine=config.POSTGRES_ENGINE)
bot: Final[Bot] = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp: Final[Dispatcher] = Dispatcher(storage=RedisStorage.from_url(config.REDIS_URL))

main_router: Final[Router] = Router(name="main")
dp.include_router(main_router)

