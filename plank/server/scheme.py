from __future__ import annotations
import copy
from plank import logger
from typing import Optional, Any, Type, Dict, TYPE_CHECKING, TypeVar, Generic, Union
from plank.server.define import ServerSide, ClientSide

if TYPE_CHECKING:
    from plank.server.api import CommonAPI


class SchemeHelper:
    __protocol__ = NotImplemented

    @property
    def api(self):
        return self.__api

    @property
    def attributes(self):
        return self.__attributes

    def __init__(self, api: CommonAPI):
        self.__api = api
        self.__attributes = {}

    def set(self, **attrs):
        self.__attributes.update(attrs)
        return self

    def get(self, key: str, default: Optional[Any] = None):
        return self.__attributes.get(key, default)

    def copy(self, api: CommonAPI)->SchemeHelper:
        a_copy = copy.copy(self)
        a_copy.__api = api
        a_copy.__attributes = self.__attributes
        return a_copy

    def call(self, *args, **kwargs):
        raise NotImplementedError


WrapperType = TypeVar("WrapperType", ServerSide, ClientSide)

class SchemeSelector(Generic[WrapperType]):

    def __init__(self, mapping: Union[Dict, SchemeManager]):
        self.__mapping = mapping

    def __getitem__(self, item: str)->WrapperType:
        manager = SchemeManager.default()
        scheme_helper = manager.get(protocol=item)

        if issubclass(WrapperType, ServerSide):
            return scheme_helper.__server__()
        else: #client
            return scheme_helper.__client__()


class SchemeManager:
    @classmethod
    def default(cls, *, key="__singleton__")->SchemeManager:
        if not hasattr(cls, key):
            setattr(cls, key, cls())
        return getattr(cls, key)

    def __init__(self):
        self.__helper_types = {}

    def register(self, helper_type: Type[SchemeHelper], protocol: Optional[str] = None):
        protocol = protocol or helper_type.__protocol__
        self.__helper_types[protocol] = helper_type

    def get(self, protocol: str)->SchemeHelper:
        try:
            return self.__helper_types[protocol]
        except KeyError as e:
            logger.error("SchemeManager did not register `SchemeHelper` for `http`, please check it.")
            raise e

    def contains(self, protocol: str):
        return protocol in self.__helper_types

