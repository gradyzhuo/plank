from __future__ import annotations
from polymath.server.message import Request, Response
from polymath.app.context import Context
from polymath.utils.path import clearify

class Backend:

    def routing_path(self)->str:
        raise NotImplementedError

    async def receive(self, request: Request) -> Response:
        pass