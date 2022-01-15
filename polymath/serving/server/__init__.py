from __future__ import annotations
from polymath.serving.backend import Backend
from typing import Optional

class Server:

    @property
    def address(self)->str:
        return self.__address

    def listen(self):
        raise NotImplementedError

    def __init__(self, address: str):
        self.__address = address
        self.__registered_backends = {}

    def add_backend(self, key: str, backend: Backend):
        self.__registered_backends[key] = backend

    def remove_backend(self, key: str)->Backend:
        return self.__registered_backends.pop(key)

    def backend(self, key: str)->Optional[Backend]:
        return self.__registered_backends.get(key)

    def __getitem__(self, key: str)->Backend:
        return self.__registered_backends[key]

    def __setitem__(self, key: str, backend: Backend):
        self.register(key=key, backend=backend)