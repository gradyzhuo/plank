from __future__ import annotations

from typing import Any

from plank.server.message import Request, Response


class Action:

    def routing_path(self) -> str:
        raise NotImplementedError

    async def receive(self, request: Request) -> Response:
        pass

    def reverse(self, response: Response) -> Any:
        pass
