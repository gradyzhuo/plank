from __future__ import annotations

from collections import namedtuple
from typing import Optional, Any, Dict, Union, List, Tuple, AnyStr, Iterable

from plank.app import Application
from plank.server.api import BoundedAPI, CallableAPI
from plank.server.scheme import SchemeHelper


class BindAddress(namedtuple("BindAddress", ("host", "port"))):
    def description(self) -> str:
        key = f"{self.host}"
        if self.port is not None:
            return f"{key}:{self.port}"
        return key


class Server:
    def launch(self, **options):
        raise NotImplementedError


class ApplicationServer(Server):
    __protocol__ = None

    class Delegate(Application.Delegate):
        def server_did_startup(self, server: Server): pass

        def server_did_shutdown(self, server: Server): pass

    @property
    def delegate(self) -> ApplicationServer.Delegate:
        return self.__delegate

    @property
    def build_version(self) -> str:
        return self.application.build_version

    @property
    def application(self) -> Application:
        return self.__application

    @property
    def support_protocol(self) -> str:
        protocol = self.__class__.__protocol__
        assert protocol is not None, "The `__protocol__` of Server class supported is needed."
        return protocol

    @property
    def scheme_helpers(self) -> List[Tuple[str, SchemeHelper]]:
        return self.__scheme_helpers

    @property
    def launched(self) -> bool:
        return self.__launched

    @property
    def launch_options(self) -> Dict[AnyStr, Any]:
        return self.__launch_options

    @launch_options.setter
    def launch_options(self, new_value: Optional[Dict[AnyStr, Any]]):
        self.__launch_options = new_value

    def __init__(self, application: Application, delegate: Optional[ApplicationServer.Delegate] = None):
        self.__application = application
        self.__scheme_helpers = []
        self.__launch_options = None
        self.__launched = False

        if delegate is None and isinstance(application.delegate, self.__class__.Delegate):
            self.__delegate = application.delegate
        else:
            self.__delegate = delegate or self.__class__.Delegate()

    def launch(self, **options):
        self.application.launch(**options)
        self.__launched = True

        for name, service in self.application.services.items():
            scheme_helpers = service.get_scheme_helpers(scheme=self.support_protocol)
            self.__scheme_helpers.extend(scheme_helpers)

        self.did_launch()

    def did_launch(self):
        for name, helper in self.scheme_helpers:
            self.__handle_scheme__(scheme_helper=helper, name=name)

    def __safe_call_delegate_method(self, method_name: str) -> Any:
        if hasattr(self.delegate, method_name):
            method = getattr(self.delegate, method_name)
            return method(self)

    def did_startup(self):
        self.application._server_did_startup(server=self)
        self.__safe_call_delegate_method(method_name="server_did_startup")

    def did_shutdown(self):
        self.__application._server_did_shutdown(server=self)
        self.__safe_call_delegate_method(method_name="server_did_shutdown")

    def add_api(self, api: Union[BoundedAPI, CallableAPI], name: Optional[str] = None):
        name = name or api.end_point.__name__
        self.__scheme_helpers.append((name, getattr(api, self.support_protocol)))

    def add_apis(self, apis: Iterable[Tuple[str, Union[BoundedAPI, CallableAPI]]]):
        for name, api in apis:
            self.add_api(api=api, name=name)

    def __handle_scheme__(self, scheme_helper: SchemeHelper, name: Optional[str]):
        pass
