import logging
from logging.config import fileConfig

fileConfig("src/logging_conf.ini")
logger = logging.getLogger()
