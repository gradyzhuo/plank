from __future__ import annotations

from typing import Optional

from plank.server import Server, BindAddress


class InlineServer(Server):
    __listened_servers = {}

    @classmethod
    def listened_server(cls, address: BindAddress) -> Optional[InlineServer]:
        return cls.__listened_servers.get(address.description())

    def listen(self, **app_launch_options):
        super().listen(**app_launch_options)
        type(self).__listened_servers[self.bind_address.description()] = self
