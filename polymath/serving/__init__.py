from __future__ import annotations
from typing import Dict, Any, Type, Optional
from polymath.serving.connector import Connector
from polymath.serving.message import Request
from functools import reduce
import inspect

class Serving:
    @classmethod
    def proxy(cls, connector: Connector)->ServingProxy:
        from polymath.serving.extension import Extension
        attrs = {}
        if issubclass(cls, Extension):
            mro = inspect.getmro(cls)
            base_cls = mro[1]
            members = inspect.getmembers(base_cls)
            for name, member in members:
                if hasattr(member, "__qualname__") \
                        and member.__qualname__.startswith(base_cls.__name__) \
                        and inspect.isfunction(member):
                    signature = inspect.signature(member)
                    filtered_keys = filter(lambda item: item != "self", signature.parameters.keys())
                    parameters = reduce(lambda result, key: result + f"{key!r}: {key},", filtered_keys, "")
                    exec(f"""def _{name}({', '.join(signature.parameters.keys())}):
    return self.perform(arguments={{"method":"{name}",{parameters}}})""")
                    attrs[name] = eval(f"_{name}")
        proxy_cls = type(f"{cls.__name__}ServingProxy", (ServingProxy, ), attrs)
        return proxy_cls(serving_cls=cls, connector=connector)

    def perform(self, arguments: Dict[str, Any])->Any:
        raise NotImplementedError

class ServingProxy(Serving):

    @property
    def headers(self)->Dict[str, str]:
        return self.__headers

    def __init__(self, serving_cls: Type[Serving], connector: Connector, headers: Optional[Dict[str, str]]=None):
        self.__serving_cls = serving_cls
        self.__connector = connector
        self.__headers = headers or {}

    def perform(self, arguments: Dict[str, Any]) -> Any:
        request = Request(arguments=arguments, headers=self.__headers)
        response = self.__connector.send(request)
        return response.value