from __future__ import annotations
import inspect
from typing import List, Any, Optional, NoReturn
from pydantic import BaseModel
from polymath.app.context import Context
from polymath.serving import Serving
from polymath.server.backend.wrapper import WrapperBackend

class Service(Serving):

    @classmethod
    def from_name(cls, name: str, plugin: Optional[str]=None)->Service:
        context = Context.standard(namespace=Service.__qualname__)
        name = name if plugin is None else f"{plugin}.{name}"
        return context.get(key=name)

    @classmethod
    def register(cls, service: Service, name: Optional[str]=None, plugin: Optional[str]=None)->NoReturn:
        name = name or service.name()
        name = name if plugin is None else f"{plugin}.{name}"
        context = Context.standard(namespace=Service.__qualname__)
        context.set(key=name, value=service)

    @classmethod
    def registered(cls, plugin: Optional[str]=None)->List[Service]:
        plugin = plugin or ""
        context = Context.standard(namespace=Service.__qualname__)
        return [
            service
            for key, service in context.items()
            if key.startswith(plugin)
        ]

    def __init__(self, name: str, serving_path: Optional[str]=None):
        self.__name = name
        self.__serving_path = serving_path

    def name(self)->str:
        return self.__name

    def serving_path(self) -> Optional[str]:
        return None if self.__serving_path is None else Context.standard().reword(self.__serving_path)

    def perform(self, arguments:BaseModel) -> Any:
        raise NotImplementedError()

    def get_backends(self)->List[WrapperBackend]:
        return [
            member
            for name, member in inspect.getmembers(self)
            if isinstance(member, WrapperBackend) and not hasattr(member, "__qualname__")
        ]

