from typing import Callable, NoReturn


class ServerSide:

    def incoming(self, *args, **kwargs)->Callable[[Callable], NoReturn]:
        raise NotImplementedError

    def outgoing(self, *args, **kwargs):
        raise NotImplementedError


class ClientSide:

    def sending(self):
        raise NotImplementedError

    def received(self):
        raise NotImplementedError