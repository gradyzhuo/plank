from typing import Callable, Any, Optional

from plank.server.action import Action


class WrapperAction(Action):

    def __init__(
            self,
            path: str,
            end_point: Callable,
            response_reverser: Optional[Callable] = None
    ):
        self.__path = path
        self.__end_point = end_point
        self.__response_reverser = response_reverser

    def end_point(self) -> Callable:
        return self.__end_point

    def routing_path(self) -> str:
        return self.__path

    def set_response_reverser(self, func: Callable[[Any], Any]):
        self.__response_reverser = func

    def reverse(self, response: Any) -> Any:
        if self.__response_reverser is None:
            return response
        return self.__response_reverser(response)

    def __call__(self, *args, **kwargs):
        return self.__end_point(*args, **kwargs)
