from __future__ import annotations
from plank.server.message import Request, Response
from pydantic import BaseModel
from typing import Type, Callable, Any
from plank.app.context import Context
from plank.utils.path import clearify

class Action:

    def routing_path(self)->str:
        raise NotImplementedError

    async def receive(self, request: Request) -> Response:
        pass

    def reverse(self, response: Response) -> Any:
        pass

