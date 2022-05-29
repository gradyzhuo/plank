from __future__ import annotations
import inspect
from typing import List, Any, Optional, NoReturn
from pydantic import BaseModel
from polymath.app.context import Context
from polymath.server.connector import Connector
from polymath.server.message import Request
from polymath.serving import Serving
from polymath.server.backend.wrapper import WrapperBackend

class ServiceProxy(Serving):

    class Invoker:
        def __init__(self, proxy: ServiceProxy, method: str):
            self.__proxy = proxy
            self.__method = method

        def __call__(self, **kwargs)->Any:
            request = Request(arguments=kwargs)
            response = self.__proxy.connector.send(request)
            return response.value

    @property
    def connector(self)->Connector:
        return self.__connector

    def __init__(self, connector: Connector):
        self.__connector = connector

    def perform(self, arguments:BaseModel) -> Any:
        request = Request(arguments=arguments.dict())
        response = self.__connector.send(request)
        return response.value

    def __getattribute__(self, method_name:str)->Invoker:
        members = inspect.getmembers(self.__class__)
        # for name, member in members:
        #     if hasattr(member, "__qualname__"):
        #         if not member.__qualname__.startswith("object") and member.__qualname__ != "type":
        #             #繼承來的
        #             attrs[name] = member
        #     else:
        #         #這個class自定義
        #         attrs[name] = member
        return ServiceProxy.Invoker(proxy=self, method=method_name)


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



    @classmethod
    def proxy(cls, connection_url: str):
        # members = inspect.getmembers(cls)
        # members[0]
        # attrs = {}
        # for name, member in members:
        #     # filter with builtin __[NAME]__ methods
        #     if re.match(r"__\w+__", name) != None:
        #         continue
        # 
        #     if hasattr(member, "__qualname__"):
        #         if not member.__qualname__.startswith("object") and member.__qualname__ != "type":
        #             #繼承來的
        #             attrs[name] = member
        #     else:
        #         #這個class自定義
        #         attrs[name] = member


        # for name, member in members:
        #     # if hasattr(member, "__qualname__") \
        #     #         and member.__qualname__.startswith(base_cls.__name__) \
        #     #         and inspect.isfunction(member):
        #     #     signature = inspect.signature(member)
        #     #     filtered_keys = filter(lambda item: item != "self", signature.parameters.keys())
        #     #     parameters = reduce(lambda result, key: result + f"{key!r}: {key},", filtered_keys, "")
        #     #     code = f"""def _{name}({', '.join(signature.parameters.keys())}):
        #     #     return self.perform(arguments={{"method":"{name}",{parameters}}})"""
        #     #     exec(code)
        #     #     attrs[name] = eval(f"_{name}")
        #     if hasattr(member, "__qualname__") and name == "perform":
        #         import importlib
        #         importlib.__import__()
        # 
        #     else:
        #         this_class_implements_attrs[name] = member
        # 
        # attrs = {}
        # attrs.update(this_class_implements_attrs)
        # proxy_cls = type(f"{cls.__name__}ServingProxy", (cls,), attrs)
        configuration_info = None
        if connection_url is not None:
            connector = Connector.get_type(url=connection_url)
        elif configuration_info is not None:
            pass
        else:
            url = "inline://service:8224"
            connector = Connector.get_type(url=url)
            pass
        return proxy_cls(serving_cls=cls, connector=connector)

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

