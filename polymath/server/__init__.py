from __future__ import annotations
from typing import Optional, Dict, Callable, TYPE_CHECKING, NoReturn, Any
from collections import namedtuple
from polymath.server.backend import Backend
from polymath.utils.path import clearify

if TYPE_CHECKING:
    from polymath.serving import Service
    from polymath.app import Application

class ServerDelegate:
    def server_did_startup(self, server: Server): pass
    def server_did_shutdown(self, server: Server): pass


class BindAddress(namedtuple("BindAddress", ("host", "port"))):
    def description(self)->str:
        key = f"{self.host}"
        if self.port is not None:
            return f"{key}:{self.port}"
        return key

class Server:

    @classmethod
    def by_host(cls, host: str, application: Application, port: Optional[int]=None):
        return cls(binding=BindAddress(host=host, port=port), application=application)

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

    def __init__(self, binding: BindAddress, application: Application, delegate: Optional[ServerDelegate]=None):
        self.__bind_address = binding
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

    def listen(self, **app_launch_options):
        self.application.launch(**app_launch_options)

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