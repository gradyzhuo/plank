from __future__ import annotations
from copy import copy
from typing import Optional, Type, Callable, Dict, Any
from polymath.server.backend.wrapper import WrapperBackend
from polymath.serving.service import Service
from polymath.utils.path import clearify

class BackendDescriptor:

    def backend_init_args(self)->Dict[str, Any]:
        return self.__meta_args

    def __init__(self,
                 path: str,
                 end_point: Callable,
                 **kwargs
                 ):
        self.__path = path
        self.__meta_args = kwargs
        self.__unbound_end_point = end_point
        self.__api_instances = {}

    def __get__(self, instance:Service, owner:Type[Service])->WrapperBackend:
        key = id(instance)
        end_point = self.__unbound_end_point.__get__(instance, owner)
        self.__meta_args["end_point"] = end_point
        if key not in self.__api_instances.keys():
            kwargs = copy(self.backend_init_args())
            instance_serving_path = instance.serving_path()
            if instance_serving_path is not None:
                kwargs["path"] = f"/{clearify(instance.serving_path())}/{clearify(self.__path)}"
            else:
                kwargs["path"] = f"/{clearify(self.__path)}"
            api = self.make_backend(**kwargs)
            self.__api_instances[key] = api
        return self.__api_instances[key]

    def make_backend(self, path: str, end_point: Callable, **kwargs)->Backend:
        from polymath.server.backend.wrapper import WrapperBackend
        return WrapperBackend(path=path, end_point=end_point, descriptor=self)