from __future__ import annotations
from polymath.serving.server import Server

class InlineServer(Server):
    listened_servers = {}

    def __init__(self):
        super().__init__(address="local")

    def listen(self):
        InlineServer.listened_servers[self.address] = self
