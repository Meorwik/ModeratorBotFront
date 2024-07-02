from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from datetime import datetime, timedelta
from redis.asyncio import Redis
from data.config import config
from typing import Dict, Final
from pytz import timezone
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
        job_defaults = {'misfire_grace_time': 5}
        return job_defaults

    def __setup_timezone(self):
        tz = timezone('Etc/GMT-5')
        return tz

    def __init__(self):
        jobstores: Dict = self.__setup_redis_job_store()
        job_defaults: Dict = self.__setup_job_defaults()
        scheduler_timezone = self.__setup_timezone()
        self.__scheduler: AsyncIOScheduler = AsyncIOScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            timezone=scheduler_timezone
        )

    @property
    def engine(self):
        return self.__scheduler

    async def init(self):
        self.__scheduler.start()


