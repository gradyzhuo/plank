from typing import Optional

def clearify(path: str, prefix:Optional[bool]=None, suffix:Optional[bool]=None)->str:
    prefix = prefix if prefix is not None else True
    suffix = suffix if suffix is not None else True
    if prefix:
        path = path if not path.startswith("/") else path[1:]
    if suffix:
        path = path if not path.endswith("/") else path[:-1]
    return path