from enum import Enum, EnumMeta
import time
from typing import Optional
from polymath import logger
from functools import wraps
from contextlib import contextmanager
import asyncio


def show_deprecated_warnning(deprecated_namespace:str, instead_namespace:str, level:str="module"):
    logger.warn(f"The {level} `{deprecated_namespace}` was deprecated, `{instead_namespace}` instead.")

class ErrorMeta(EnumMeta):
    def __call__(cls, value, names=None, *, module=None, qualname=None, type=None, start=1):
        if value.__class__ is str:
            for e in cls:
                if e.value[0] == value.upper():
                    value = e.value
                    break
        return super().__call__(value, names=names, module=module, qualname=qualname, type=type, start=start)
        
    
class Error(Enum, metaclass=ErrorMeta):
    @property
    def name(self):
        return self._value_[0]

def timing(func):
    @contextmanager
    def wrapping_logic():
        start_ts = time.time()
        yield
        dur = (time.time() - start_ts ) * 1000.0
        logger.info('{:s} function took {:.3f} ms'.format(func.__name__, (dur)))

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic():
                return func(*args, **kwargs)
        else:
            async def tmp():
                with wrapping_logic():
                    return (await func(*args, **kwargs))
            return tmp()
    return wrapper
