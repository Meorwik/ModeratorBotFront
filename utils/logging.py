from logging import StreamHandler, Logger, basicConfig, INFO
from typing import Final

basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=INFO)


DATABASE_LOGS_HANDLER: Final[StreamHandler] = StreamHandler()
DATABASE_LOGGER: Final[Logger] = Logger("Database")
DATABASE_LOGGER.addHandler(DATABASE_LOGS_HANDLER)
