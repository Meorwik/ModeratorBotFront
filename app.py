from loader import dp, bot, postgres, commands, scheduler
from aiogram import Dispatcher
from data.config import config
from redis import Redis
import handlers
import asyncio
import utils


async def a():
    print(123)


async def setup_scheduler():
    await scheduler.init()

    scheduler.engine.add_job(a, 'cron', minute="*", coalesce=True)


async def setup_admin():
    admin = await postgres.get_admin()
    redis: Redis = Redis.from_url(config.REDIS_URL)
    redis.set("admin", admin.id)
    redis.close()


async def app(dispatcher: Dispatcher):
    await bot.set_my_commands(commands)
    await postgres.init()
    await setup_admin()
    await setup_scheduler()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(app(dp))
