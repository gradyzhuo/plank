from typing import Callable
from plank.server.action import Action

class WrapperAction(Action):

    def __init__(
            self,
            path: str,
            end_point: Callable
    ):
        self.__path = path
        self.__end_point = end_point

    def end_point(self)->Callable:
        return self.__end_point

    def routing_path(self) ->str:
        return self.__path

    def __call__(self, *args, **kwargs):
        return self.__end_point(*args, **kwargs)