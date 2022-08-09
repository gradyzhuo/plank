from __future__ import annotations
from typing import Optional, Dict, Any
from pathlib import Path
from collections import namedtuple
from polymath.server.backend import Backend
from polymath.app import Application

class BindAddress(namedtuple("BindAddress", ("host", "port"))):
    def description(self)->str:
        key = f"{self.host}"
        if self.port is not None:
            return f"{key}:{self.port}"
        return key

class Server:
    class Delegate(Application.Delegate):
        def server_did_startup(self, server: Server): pass

        def server_did_shutdown(self, server: Server): pass
    #
    @classmethod
    def build(cls, name: str, version: str, delegate: Server.Delegate, workspace: Path, build_version: Optional[str] = None, configuration_path:Optional[Path]=None, **server_kwargs)->Server:
        application = Application.construct(name=name, version=version, build_version=build_version, delegate=delegate, workspace_path=workspace, configuration_path=configuration_path)
        return cls(application=application, **server_kwargs)

    @property
    def delegate(self)->Server.Delegate:
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

    def __init__(self, application: Application, delegate: Optional[Server.Delegate]=None):
        self.__bind_address = None
        self.__registered_backends = {}
        self.__application = application

        if delegate is None and isinstance(application.delegate, Server.Delegate):
            self.__delegate = application.delegate
        else:
            self.__delegate = delegate or Server.Delegate()

    def add_backend(self, backend: Backend):
        self.__registered_backends[backend.path] = backend

    def add_backends(self, *backends: Backend):
        for backend in backends:
            self.add_backend(backend=backend)

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