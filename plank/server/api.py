from __future__ import annotations

import logging
from typing import Callable, Any, Type,  Union, TYPE_CHECKING, Optional, Dict
from plank.server.scheme import SchemeHelper, SchemeManager
from plank.utils.function import can_bound
from plank.server.define import ServerSide, ClientSide
from plank.server.scheme import SchemeSelector
from functools import reduce
from collections import namedtuple

SupportScheme = namedtuple("SupportScheme", ["protocol", "scheme"])

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
    def server(self)->SchemeSelector[ServerSide]:
        return SchemeSelector[ServerSide]()

    @property
    def client(self)->SchemeSelector[ClientSide]:
        return SchemeSelector[ClientSide]()


    def __init__(self, end_point: Callable):
        self.__end_point = end_point
        self.__scheme_helpers = []
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
                _api = BoundedAPI(end_point)
                _api.__scheme_helpers = [
                    SupportScheme(protocol=protocol, scheme=scheme.copy(api=_api))
                    for protocol, scheme in self.__scheme_helpers
                ]
                self.__bounded_apis[key] = _api
            return self.__bounded_apis[key]

    def catch(self, exception_type: Type[Exception]):
        def wrap(func: Callable[[Exception], Any]):
            pass
        return wrap

    def contains(self, protocol: Union[str, Type[SchemeHelper]])->bool:
        protocol = protocol if isinstance(protocol, str) else protocol.__protocol__
        return reduce(lambda result, item: result or item[0] == protocol, self.__scheme_helpers, False)


    def set_scheme(self, scheme: SchemeHelper, protocol: Optional[str]=None):
        protocol = protocol or scheme.__protocol__
        if not self.contains(protocol=protocol):
           self.__scheme_helpers.append(SupportScheme(protocol=protocol, scheme=scheme))
        else:
            logging.warn(f"Repeated for setting protocol {protocol} in API {self.name}.")


    def __getitem__(self, attr: str) -> SchemeHelper:
        for protocol, scheme in self.__scheme_helpers:
            if protocol == attr:
                return scheme
        raise AttributeError(f"API[{self.name}] did not support `{attr}`.")

    def __getattr__(self, protocol: str) -> SchemeHelper:
        try:
            scheme_helper = self[protocol]
        except AttributeError as e:
            helper_type = SchemeManager.default().get(protocol=protocol)
            scheme_helper = helper_type(api=self)
            self.__protocol_helpers[protocol] = scheme_helper
        return scheme_helper




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
    
class MirrorAPI:

    def __init__(self, reference: Union[CommonAPI, CallableAPI, BoundedAPI]):
        self.__reference = reference

    def __getattr__(self, protocol: str) -> SchemeHelper:
        return self.__reference.__getattr__(protocol=property)

    
