from __future__ import annotations

import copy
import os
import re
import threading
from copy import copy
from typing import List, Tuple, Any, Optional, Union, Iterable, Dict

_Context__singleton_key = "__Context"

class Context:
    @classmethod
    def standard(cls, namespace: Optional[str]=None) -> Context:
        namespace = namespace or "main"
        key = f"{_Context__singleton_key}.{namespace}"
        lock = threading.Lock()
        if not hasattr(cls, key):
            with lock:
                obj = cls(namespace=namespace)
                setattr(cls, key, obj)
        return getattr(cls, key)

    @classmethod
    def namespaces(cls, prefix: Optional[str]=None)->List[str]:
        prefix = f"{_Context__singleton_key}.{prefix}" if prefix is not None else _Context__singleton_key
        filtered_singleton_keys  = filter(lambda key: key.startswith(prefix), cls.__dict__.keys())
        return [key.replace(f"{_Context__singleton_key}.", "") for key in filtered_singleton_keys]

    @property
    def namespace(self)->str:
        return self.__namespace

    def __init__(self, namespace: str):
        self.__namespace = namespace
        self.__contexts:Dict[str, Any] = {}
        self.__rx = r'\$\{(?P<VAR>[a-z A-Z]{1}[._\w]+)\}'

    def keys(self)->List[str]:
        return list(self.__contexts.keys())

    def values(self)->List[Any]:
        return list(self.__contexts.values())

    def items(self)->List[Tuple[str, Any]]:
        return [(key, value) for key, value in self.__contexts.items()]

    def dict(self)->Dict[str, Any]:
        return copy(self.__contexts)

    def set(self, key: str, value: Any):
        self.__contexts[key] = value

    def setdefault(self, key:str, default: Any)->Any:
        return self.__contexts.setdefault(key, default)

    def get(self, key: str, default: Optional[Any]=None, reword: Optional[bool]=None)-> Optional[Any]:
        value = self.__contexts.get(key, default)
        reword = reword if reword is not None else True
        return self.reword(value) if reword else value

    def remove(self, key: str):
        del self.__contexts[key]

    def update(self, _m: Union[Context, Dict, Iterable], **kwargs):
        if isinstance(_m, Context):
            self.__contexts.update(_m.__contexts)
        else:
            self.__contexts.update(_m, **kwargs)

    def __replace_var(self, string, replaced=lambda var_name: var_name):
        def replaces(matchobj):
            variable_key = matchobj.groupdict()["VAR"]
            return replaced(variable_key)
        return re.sub(self.__rx, replaces, str(string))

    def _reword(self, var: str, extra_info:Dict[str, Any]=None)->Any:
        grounds_dict = dict([item for item in self.items() if isinstance(item[1], (str, int, float, bool)) ])
        extra_info = extra_info or {}
        grounds_dict.update(os.environ)
        grounds_dict.update(extra_info)
        if self != Context.standard():
            grounds_dict.update(Context.standard().__contexts)
        result = grounds_dict.get(var) \
                 or self.__replace_var(var, replaced=lambda var_name: grounds_dict.get(var_name, f"${{{var_name}}}"))
        return result

    def reword(self, var: str, extra_info:Dict[str, Any]=None)->Any:
        if not isinstance(var, str):
            return var
        result = var
        match_object = self.can_reword(result)
        previous_var_name = None
        while match_object is not None:
            var_name = match_object["VAR"]
            if previous_var_name != var_name:
                previous_var_name = var_name
            else:
                break
            result = self._reword(result, extra_info)
            match_object = self.can_reword(result)
        return result

    def can_reword(self, var: str)->Optional[re.Match]:
        if type(var) is not str:
            return None
        return re.search(self.__rx, var)