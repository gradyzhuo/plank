import inspect
from typing import Callable, Any, Type, Protocol

def can_bound(f: Callable) -> bool:
    return inspect.isfunction(f) and f.__name__ != f.__qualname__ and "<lambda>" != f.__name__


def bound_if_needed(f: Callable[[Any], Any], instance: Any, owner: Type[Any]):
    if f is None:
        return None

    if can_bound(f):
        # need bounding
        return f.__get__(instance, owner)
    else:
        return f