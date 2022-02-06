import time
import asyncio
import nest_asyncio
from functools import wraps
from contextlib import contextmanager
from polymath import logger

nest_asyncio.apply()

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
            return asyncio.run(func(*args, **kwargs))
    return wrapper