from polymath.serving.server import Server
from polymath.serving.server.inline import InlineServer
from polymath.serving.backend import Backend
from polymath.serving.message import Request, Response
from polymath.serving.connector import Connector

class InlineConnector(Connector):

    @property
    def server(self)->Server:
        return self.__server

    @property
    def backend(self)->Backend:
        return self.__backend

    # inline://{address}/{service}
    def __init__(self, service_name: str):
        url = f"inline://local/{service_name}"
        super().__init__(url=url)
        self.__server = InlineServer.listened_servers[self.address]
        self.__backend = self.__server.backend(service_name)

    def send(self, request: Request) -> Response:
        return self.backend.receive(request=request)
