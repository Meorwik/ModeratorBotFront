from loader import dp, bot, postgres, commands
from aiogram import Dispatcher
from data.config import config
from redis import Redis
import handlers
import asyncio
import utils


async def on_startup(dispatcher: Dispatcher):
    await bot.set_my_commands(commands)
    await postgres.init()
    admin = await postgres.get_admin()
    redis: Redis = Redis.from_url(config.REDIS_URL)
    redis.set("admin", admin.id)
    redis.set("is_admin_busy", bytes(False))
    redis.close()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(on_startup(dp))
