from __future__ import annotations
from polymath.server.message import Request, Response

class Backend:
    def path(self)->str:
        raise NotImplementedError

    async def receive(self, request: Request) -> Response:
        pass