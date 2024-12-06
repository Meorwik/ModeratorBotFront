from loader import dp, bot, postgres, commands, scheduler
from aiogram import Dispatcher
from data.config import config
from redis import Redis
import handlers
import asyncio
import utils


async def setup_admin():
    admin = await postgres.get_admin()
    redis: Redis = Redis.from_url(config.REDIS_URL)
    redis.set("admin", admin)
    redis.close()


async def app(dispatcher: Dispatcher):
    await bot.set_my_commands(commands)
    await postgres.init()
    await setup_admin()
    await scheduler.init()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(app(dp))
