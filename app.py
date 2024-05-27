from loader import dp, bot, postgres
from aiogram import Dispatcher
import handlers
import asyncio
import utils


async def on_startup(dispatcher: Dispatcher):
    await postgres.init()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(on_startup(dp))
