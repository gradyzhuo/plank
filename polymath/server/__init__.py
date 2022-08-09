from __future__ import annotations
from typing import Optional, Dict, Callable, TYPE_CHECKING, NoReturn, Any
from collections import namedtuple
from polymath.server.backend import Backend
from polymath.utils.path import clearify

if TYPE_CHECKING:
    from polymath.serving import Service
    from polymath.app import Application

class ServerDelegate(Application.Delegate):
    def server_did_startup(self, server: Server): pass
    def server_did_shutdown(self, server: Server): pass


class BindAddress(namedtuple("BindAddress", ("host", "port"))):
    def description(self)->str:
        key = f"{self.host}"
        if self.port is not None:
            return f"{key}:{self.port}"
        return key

class Server:
    #
    @classmethod
    def build(cls, name: str, version: str, delegate: ServerDelegate, build_version: Optional[str] = None, **server_kwargs)->Server:
        application = Application(name=name, version=version, delegate=delegate, build_version=build_version)
        return cls(application=application, **server_kwargs)

    @property
    def delegate(self)->ServerDelegate:
        return self.__delegate

    @property
    def bind_address(self)->BindAddress:
        return self.__bind_address

    @property
    def application(self)->Application:
        return self.__application

    @property
    def backends(self)->Dict[str, Backend]:
        return self.__registered_backends

    def __init__(self, application: Application, delegate: Optional[ServerDelegate]=None):
        self.__bind_address = None
        self.__registered_backends = {}
        self.__application = application

        if delegate is None and isinstance(application.delegate, ServerDelegate):
            self.__delegate = application.delegate
        else:
            self.__delegate = delegate or ServerDelegate()

    def add_backend(self, backend: Backend):
        self.__registered_backends[backend.path()] = backend

    def add_backends(self, *backends: Backend):
        for backend in backends:
            self.add_backend(backend=backend)

    def add_backends_by_service(self, service: Service):
        backends = service.get_backends()
        self.add_backends(*backends)

    def remove_backend(self, path: str)->Backend:
        return self.__registered_backends.pop(path)

    def backend(self, key: str)->Optional[Backend]:
        return self.__registered_backends.get(key)

    def launch(self, **options):
        self.application.launch(**options)

    def listen(self, address: BindAddress):
        self.__bind_address = address

    def __safe_call_delegate_method(self, method_name: str)->Any:
        if hasattr(self.delegate, method_name):
            method = getattr(self.delegate, method_name)
            return method(self)

    def did_startup(self):
        self.application._server_did_startup(server=self)
        self.__safe_call_delegate_method(method_name="server_did_startup")

    def did_shutdown(self):
        self.__application._server_did_shutdown(server=self)
        self.__safe_call_delegate_method(method_name="server_did_shutdown")