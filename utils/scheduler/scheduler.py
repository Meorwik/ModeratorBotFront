from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from datetime import datetime, timedelta
import asyncio


async def example_task():
    print(f'Task executed at {datetime.now()}')


class Scheduler:

    def __init__(self):
        self.__scheduler: AsyncIOScheduler = AsyncIOScheduler()

    @property
    def engine(self):
        return self.__scheduler

    async def init(self):
        self.__scheduler.start()

    async def setup_redis_job_store(self):
        redis_job_store: RedisJobStore = RedisJobStore(url="redis://default:CUOsirlqHxMfyGJKPGhtxrFABMZEOyZx@roundhouse.proxy.rlwy.net:59131")
        self.__scheduler.add_jobstore(redis_job_store)
