import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
COMMON_BASE_PATH = "logs/"
COMMON_LOG_FILE = "{0}{1}".format(COMMON_BASE_PATH,"mrcnn.log")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler(fileName):
    file_handler = TimedRotatingFileHandler(fileName, encoding = "UTF-8", when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler

def getLogger(loggerName):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG) # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(COMMON_LOG_FILE))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger

def getNewFileLogger(loggerName, loggerFile = "common.log"):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG) # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler("{0}{1}".format(COMMON_BASE_PATH,loggerFile)))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger