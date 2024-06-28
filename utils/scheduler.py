from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from data.config import config
from datetime import datetime, timedelta
from typing import Dict, Final
from redis.asyncio import Redis
import asyncio


class Scheduler:
    def __setup_redis_job_store(self):
        jobs_key: Final[str] = 'apscheduler.jobs'
        run_times_key: Final[str] = "run_times_key"

        jobstores = {
            'default': RedisJobStore(
                jobs_key=jobs_key,
                run_times_key=run_times_key,
                host=config.REDIS_JOB_STORE_DATA.HOST,
                port=config.REDIS_JOB_STORE_DATA.PORT,
                password=config.REDIS_JOB_STORE_DATA.PASSWORD
            ),
        }
        return jobstores

    def __setup_job_defaults(self):
        job_defaults = {'misfire_grace_time': 3}
        return job_defaults

    def __init__(self):
        jobstores: Dict = self.__setup_redis_job_store()
        job_defaults: Dict = self.__setup_job_defaults()
        self.__scheduler: AsyncIOScheduler = AsyncIOScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults
        )

    @property
    def engine(self):
        return self.__scheduler

    async def init(self):
        self.__scheduler.start()


