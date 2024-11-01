from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types.bot_command import BotCommand
from database.postgresql import PostgresManager
from utils.scheduler import Scheduler
from aiogram.enums.parse_mode import ParseMode
from aiogram import Bot, Dispatcher, Router
from data.config import config
from typing import Final, List

postgres: Final[PostgresManager] = PostgresManager(engine=config.POSTGRES_ENGINE)
bot: Final[Bot] = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp: Final[Dispatcher] = Dispatcher(storage=RedisStorage.from_url(config.REDIS_URL))

main_router: Final[Router] = Router(name="main")
scheduler: Final[Scheduler] = Scheduler()
dp.include_router(main_router)

commands: Final[List[BotCommand]] = [
    BotCommand(command="/start", description="Запустить / перезапустить бота")
]

# postgresql+asyncpg://postgres:123@127.0.0.1