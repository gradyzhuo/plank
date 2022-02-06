from __future__ import annotations

import re

from polymath.server.message import Request, Response
from polymath.server import Server, BindAddress
from urllib.parse import urlparse, ParseResult
from typing import Type, Dict, Union
import importlib


class Connector:
    __registered_connectors: Dict[str, Type[Connector]] = {  }

    @classmethod
    def get_type(cls, url: str)->Type[Connector]:
        url_components = urlparse(url=url)
        return cls.__registered_connectors[url_components.scheme]

    @classmethod
    def connect(cls, url: str, **kwargs)->Connector:
        connector_type = cls.get_type(url=url)
        return connector_type(url=url, **kwargs)

    @classmethod
    def register(cls, connector_type: Union[str, Type[Connector]]):
        if type(connector_type) is str:
            rx = r'(?P<namespace>[a-z A-Z]+[\._\w]+):(?P<class_name>[a-z A-Z]+[_\w]*)'
            match_obj = re.search(rx, connector_type)
            assert match_obj is not None, "The parameter `connector_type` should be formatted with {namespace}:{class_name}"
            namespace = match_obj["namespace"]
            class_name = match_obj["class_name"]
            module = importlib.import_module(namespace)
            connector_type = module.__dict__[class_name]
        cls.__registered_connectors[connector_type.support_scheme()] = connector_type

    @classmethod
    def support_scheme(cls)->str:
        raise NotImplementedError

    @property
    def address(self)->Server.BindAddress:
        return BindAddress(self.__url_components.hostname, self.__url_components.port)

    @property
    def path(self)->str:
        return self.__url_components.path

    @property
    def url_components(self)->ParseResult:
        return self.__url_components

    def __init__(self, url: str, **kwargs):
        self.__url_components = urlparse(url=url)

    def send(self, request: Request)->Response:
        raise NotImplementedError()

Connector.register(connector_type="polymath.server.connector.inline:InlineConnector")