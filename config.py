import logging
from os import getenv

ADMIN_USER = getenv('CHECKIN_ADMIN_USER', 'admin')
ADMIN_PASSWORD = getenv('CHECKIN_ADMIN_PASSWORD', object())

GOOGLE_API_KEY = getenv('CHECKIN_GOOGLE_API_KEY')

DB_HOST = getenv('CHECKIN_DB_HOST', 'localhost')
DB_PORT = int(getenv('CHECKIN_DB_PORT', 5432))
DB_USER = getenv('CHECKIN_DB_USER')
DB_PASSWORD = getenv('CHECKIN_DB_PASSWORD')
DB_NAME = getenv('CHECKIN_DB_NAME')

LOG_LEVEL = getenv('CHECKIN_LOG_LEVEL', 'INFO').upper()


def configure_logging(level=LOG_LEVEL):
    logger = logging.getLogger('checkin')
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOG_LEVEL)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger

logger = configure_logging()
