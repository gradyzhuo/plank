from __future__ import annotations
from typing import Optional, Dict, Any, Type
from polymath.app.context import Context
import re

class ConfigInfo:

    @property
    def namespace(self)->str:
        return self.__namespace

    @property
    def context(self)->Context:
        return self.__context

    @property
    def config_dict(self)->Dict[str, Any]:
        return self.__config_dict

    def __init__(self, namespace: str, config_dict: Dict[str, Any], context: Context):
        self.__namespace = namespace
        self.__config_dict = config_dict
        self.__context = context
        for key, value in config_dict.items():
            context.set(key=key, value=value)
        self.__configure__()

    def __configure__(self): pass

    def get(self, key: str, default: Optional[Any]=None, reword: Optional[bool]=None)->Optional[Any]:
        namespace = f"{self.namespace}.{key}"
        result = self.config_dict.get(namespace, default)
        reword = reword if reword is not None else False
        if type(result) is str and reword is True:
            result = self.context.reword(result)
        return result

    def set(self, key: str, value: Any):
        namespace = f"{self.namespace}.{key}"
        self.config_dict[namespace] = value
        self.context.set(key=f"{self.namespace}.{key}", value=value)

_ConfigHandlerManager__singleton_key = "__singleton"
class ConfigInfoManager:
    @classmethod
    def default(cls)->ConfigInfoManager:
        if not hasattr(cls, _ConfigHandlerManager__singleton_key):
            singleton = cls()
            setattr(cls, _ConfigHandlerManager__singleton_key, singleton)
        return getattr(cls, _ConfigHandlerManager__singleton_key)

    def __init__(self):
        self.__builtin_handlers: Dict[str, Type[ConfigInfo]] = {}
        self.__custom_handlers: Dict[str, Type[ConfigInfo]] = {}
        self.__preloaded_handler_types: Dict[str, Type[ConfigInfo]] = {}

    def load(self):
        _handler_types = {}
        _handler_types.update(self.__builtin_handlers)
        _handler_types.update(self.__custom_handlers)
        handler_types = dict(
            [(key.replace("*", "[-\w\d]+"), handler_type) for key, handler_type in _handler_types.items()])
        return handler_types

    def register_handler_type(self, namespace: str, handler_type: Type[ConfigInfo]):
        assert issubclass(handler_type, ConfigInfo), "handler_type should be inherited from ConfigHandler"
        self.__custom_handlers[namespace] = handler_type

    def unregiser_handler_type(self, namespace: str):
        del self.__custom_handlers[namespace]

    def get_handler_type(self, namespace: str, default: Optional[Type[ConfigInfo]] = None) -> Optional[
        Type[ConfigInfo]]:
        handler_types = self.load()
        for pattern, handler_type in handler_types.items():
            result = re.search(pattern, namespace)
            if result is not None:
                return handler_type
        return default
