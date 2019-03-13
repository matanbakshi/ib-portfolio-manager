import logging
from logging.config import fileConfig

fileConfig("./logging_conf.ini")
logger = logging.getLogger()
