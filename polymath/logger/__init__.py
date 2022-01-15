import logging
import os

logger = logging.getLogger()
logger.level = logging.DEBUG

def log(*items, sep=" ", level=None):
    msg = sep.join(map(lambda item: str(item), items))
    logging.log(level=level, msg=msg)

def info(*items, sep:str=" "):
    log(*items, sep=sep, level=logging.INFO)

def debug(*items, sep=" "):
    log(*items, sep=sep, level=logging.DEBUG)

def warn(*items, sep=" "):
    log(*items, sep=sep, level=logging.WARNING)

def error(*items, sep=" "):
    log(*items, sep=sep, level=logging.ERROR)





