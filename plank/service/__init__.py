from __future__ import annotations

import inspect
from typing import Optional, Union, List, Tuple, TYPE_CHECKING, Type

from plank.context import Context

from plank import logger
from plank.server.api import BoundedAPI, CommonAPI
from plank.server.scheme import SchemeHelper

if TYPE_CHECKING:
    from plank.plugin import Plugin

SERVICES_CONTEXT_KEY = "collection.services"

class Service:
    __api_names__: List[str] = []

    @property
    def plugin(self):
        if not hasattr(self, "_plugin"):
            return None
        return self._plugin

    def get_name(self)->Optional[str]:
        from plank.app import Application
        app = Application.main()
        target = None
        for name, service in app.services.items():
            if service == self:
                target = name
                break
        return target


    @classmethod
    def from_name(cls, name: str, plugin: Optional[Plugin] = None) -> Service:
        if plugin is not None:
            return plugin.services.get(name=name)
        else:
            from plank.app import Application
            app = Application.main()
            return app.services.get(name=name)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        predicate = lambda member: isinstance(member, CommonAPI)
        cls.__api_names__ = [method_name for method_name, api in inspect.getmembers(cls, predicate=predicate)]

    def get_apis(self, protocol: Optional[Union[str, Type[SchemeHelper]]] = None) -> List[Tuple[str, BoundedAPI]]:
        apis = map(lambda api_name: (api_name, getattr(self, api_name)), self.__class__.__api_names__)

        return [
            (name, api)
            for name, api in apis
            if api.contains(protocol)
        ]

    def get_scheme_helpers(self, scheme: str):
        apis = self.get_apis(protocol=scheme)
        result = [(name, getattr(api, scheme)) for name, api in apis ]
        return result

    def install(self, plugin: Plugin):
        plugin.services.add(service=self)
        self.did_install(plugin=plugin)

    def did_install(self, plugin: Plugin):
        if self.plugin is None and plugin is not None:
            self._plugin = plugin



class ServiceManager:

    @property
    def scope(self) -> Optional[str]:
        return self.__scope

    @classmethod
    def shared(cls, scope: Optional[str] = None) -> ServiceManager:
        key = "__singleton__"
        if scope is not None:
            key = f"{key}.{scope}"
        if not hasattr(cls, key):
            setattr(cls, key, cls(scope=scope))
        return getattr(cls, key)

    def __init__(self, scope: Optional[str]):
        self.__scope = scope

        if scope is not None:
            namespace = f"{SERVICES_CONTEXT_KEY}.{scope}"
        else:
            namespace = SERVICES_CONTEXT_KEY
        self.__context = Context.standard(namespace=namespace)

    def items(self) -> List[Tuple[str, Service]]:
        return self.__context.items()

    def add(self, service: Service, name: Optional[str]=None):
        name = name or f"{service.__class__.__name__}:{id(service)}"
        self.__context.set(key=name, value=service)
        log_prefix = self.__scope or "Application"
        logger.info(f"[{log_prefix}] Added service with name: {name}, instance: {service}.")

    def __iter__(self):
        return self.__context.keys()

    def get(self, name: str) -> Service:
        return self.__context.get(key=name)

    def __getitem__(self, name: str) -> Service:
        return self.get(name=name)
