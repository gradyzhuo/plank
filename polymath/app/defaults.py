from __future__ import annotations
from typing import List, Tuple, Any, Optional

_UserDefaults__singleton_key = "__singleton"

class UserDefaults:
    @classmethod
    def standard(cls, namespace: Optional[str]=None) -> UserDefaults:
        namespace = namespace or "main"
        key = f"{_UserDefaults__singleton_key}_{namespace}"
        if not hasattr(cls, key):
            obj = UserDefaults()
            setattr(cls, key, obj)
        return getattr(cls, key)

    def __init__(self):
        self.__contexts = {}

    def keys(self)->List[str]:
        return self.__contexts.keys()

    def values(self)->List[Any]:
        return self.__contexts.values()

    def items(self)->List[Tuple]:
        return self.__contexts.items()

    def set(self, key: str, value: Any):
        self.__contexts[key] = value

    def get(self, key: str, default: Optional[Any]=None)-> Optional[Any]:
        return self.__contexts.get(key, default)
