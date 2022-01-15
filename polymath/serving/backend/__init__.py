from __future__ import annotations
from polymath.serving.message import Request, Response

class Backend:
    def receive(self, request: Request) -> Response:
        pass