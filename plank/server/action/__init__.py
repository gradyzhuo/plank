from __future__ import annotations
from plank.server.message import Request, Response
from plank.app.context import Context
from plank.utils.path import clearify

class Action:

    def routing_path(self)->str:
        raise NotImplementedError

    async def receive(self, request: Request) -> Response:
        pass