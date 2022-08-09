from __future__ import annotations
from polymath.server.message import Request, Response
from polymath.app.context import Context
from polymath.utils.path import clearify

class Backend:

    @property
    def path(self)->str:
        reworded_path = Context.standard().reword(self.__routing_path__())
        clearifed_path = clearify(reworded_path)
        return f"/{clearifed_path}"

    def __routing_path__(self)->str:
        raise NotImplementedError

    async def receive(self, request: Request) -> Response:
        pass