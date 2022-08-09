from typing import Callable
from polymath.server.backend import Backend

class WrapperBackend(Backend):

    @property
    def descriptor(self):
        return self.__descriptor

    def __init__(
            self,
            path: str,
            end_point: Callable,
            descriptor
    ):
        self.__path = path
        self.__end_point = end_point
        self.__descriptor = descriptor

    def end_point(self)->Callable:
        return self.__end_point

    def routing_path(self) ->str:
        return self.__path

    def __call__(self, *args, **kwargs):
        return self.__end_point(*args, **kwargs)