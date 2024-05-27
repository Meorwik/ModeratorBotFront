from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from utils.logging import DATABASE_LOGGER, INFO

Base = declarative_base()


class DatabaseManager:
    __name__ = "DatabaseManager"

    def __repr__(self):
        return f"{self.__name__}Object - ({id(self)})"

    def __init__(self, engine, **options):
        self.engine: AsyncEngine = create_async_engine(engine)
        self.Session = async_sessionmaker(bind=self.engine)
        DATABASE_LOGGER.log(msg=f"{self.__name__} was successfully launched with {options} options", level=INFO)

