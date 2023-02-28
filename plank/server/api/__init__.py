from __future__ import annotations
from typing import Callable, Any, Type,  Union, TYPE_CHECKING, Optional, Dict
from plank.server.scheme import SchemeHelper, SchemeManager
from plank.utils.function import can_bound
from plank.server.api.node import ServerSide, ClientSide
from plank.server.api.selector import SchemeHelperSelector

class CommonAPI:

    @property
    def end_point(self) -> Callable[[Any], Any]:
        return self.__end_point

    @property
    def name(self)->str:
        return self.__end_point.__name__

    @property
    def meta(self)->Dict[str, Any]:
        return dict(self.__meta)

    @property
    def server(self)->SchemeHelperSelector[ServerSide]:
        return SchemeHelperSelector[ServerSide]()

    @property
    def client(self)->SchemeHelperSelector[ClientSide]:
        return SchemeHelperSelector[ClientSide]()


    def __init__(self, end_point: Callable):
        self.__end_point = end_point
        self.__protocol_helpers = {}
        self.__bounded_apis = {}
        self.__meta = []

    def set_meta_info(self, key: str, value: Any)->CommonAPI:
        self.__meta.append((key, value))
        return self

    def get_meta_info(self, key: str)->Optional[str]:
        result = None
        for _key, value in self.__meta:
            if _key == key:
                result = value
        return result

    def __get__(self, instance, owner):
        if instance is None and can_bound(self.__end_point):
            return self
        else:
            key = id(instance)
            if key not in self.__bounded_apis:
                end_point = self.__end_point.__get__(instance, owner)
                bound_api = BoundedAPI(end_point)
                bound_api.__protocol_helpers = {
                    protocol: helper.copy(api=bound_api)
                    for protocol, helper in self.__protocol_helpers.items()
                }
                self.__bounded_apis[key] = bound_api
            return self.__bounded_apis[key]

    def catch(self, exception_type: Type[Exception]):
        def wrap(func: Callable[[Exception], Any]):
            pass
        return wrap

    def contains(self, protocol: Union[str, Type[SchemeHelper]])->bool:
        protocol = protocol if isinstance(protocol, str) else protocol.__protocol__
        return protocol in self.__protocol_helpers.keys()

    def __getattr__(self, attr: str) -> SchemeHelper:
        protocol = attr
        if protocol not in self.__protocol_helpers.keys():
            helper_type = SchemeManager.default().get(protocol=protocol)
            protocol_helper = helper_type(api=self)
            self.__protocol_helpers[protocol] = protocol_helper
        return self.__protocol_helpers[protocol]


class CallableAPI(CommonAPI):

    def __call__(self, *args, **kwargs):
        return self.end_point(*args, **kwargs)

class BoundedAPI(CallableAPI):
    @property
    def instance(self)->Any:
        return self.end_point.__self__

    @property
    def owner(self)->Type[Any]:
        return self.instance.__class__
