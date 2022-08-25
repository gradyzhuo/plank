from __future__ import annotations
import inspect
from typing import List, Any, Optional, NoReturn, Union, TYPE_CHECKING
from pydantic import BaseModel
from plank.serving import Serving
from plank.app.context import Context
from plank.server.action.wrapper import WrapperAction

if TYPE_CHECKING:
    from plank.plugin import Plugin

class ServiceManagerable:
    def add_service(self, service: Service):
        Service.register(service, name=service.name())
    def add_services(self, *services: Service):
        for service in services:
            self.add_service(service)
    def services(self)->List[Service]:
        return Service.registered()
    def service(self, name: str)->Service:
        return Service.from_name(name=name)

class Service(Serving):

    @classmethod
    def from_name(cls, name: str, plugin: Optional[Union[str, Plugin]]=None)->Service:
        context = Context.standard(namespace=Service.__qualname__)
        if plugin is not None:
            plugin_name = plugin.name if isinstance(plugin, Plugin) else plugin
            name = f"{plugin_name}.{name}"
        return context.get(key=name)

    @classmethod
    def register(cls, service: Service, name: Optional[str]=None, plugin: Optional[Union[str, Plugin]]=None)->NoReturn:
        name = name or service.name()
        name = name if plugin is None else f"{plugin}.{name}"
        context = Context.standard(namespace=Service.__qualname__)
        context.set(key=name, value=service)

    @classmethod
    def registered(cls, plugin: Optional[Union[str, Plugin]]=None)->List[Service]:
        plugin = plugin or ""
        context = Context.standard(namespace=Service.__qualname__)
        return [
            service
            for key, service in context.items()
            if key.startswith(plugin)
        ]

    def __init__(self, name: Optional[str]=None, serving_path: Optional[str]=None):
        self.__name = name or self.__class__.__name__
        self.__serving_path = serving_path

    def name(self)->str:
        return self.__name

    def serving_path(self) -> Optional[str]:
        return None if self.__serving_path is None else Context.standard().reword(self.__serving_path)

    def perform(self, arguments:BaseModel) -> Any:
        raise NotImplementedError()

    def get_backends(self)->List[WrapperAction]:
        return [
            member
            for name, member in inspect.getmembers(self)
            if isinstance(member, WrapperAction) and not hasattr(member, "__qualname__")
        ]

