import nest_asyncio, asyncio
from polymath.server.message import Request, Response
from polymath.server import Server
from polymath.server.inline import InlineServer
from polymath.server.backend import Backend
from polymath.server.connector import Connector

nest_asyncio.apply()

class InlineConnector(Connector):

    @property
    def server(self)->Server:
        return self.__server

    @property
    def backend(self)->Backend:
        return self.__backend

    @classmethod
    def support_scheme(cls) ->str:
        return "inline"

    # needed to modify inline://local/{service}
    # request with path
    # path as service method
    def __init__(self, url: str, **kwargs):
        # url = f"inline://local/{service_name}"
        super().__init__(url=url)
        service_name = self.path
        self.__server = InlineServer.listened_server(self.address)
        print("self.__server:", self.__server)
        self.__backend = self.__server.backend(service_name)

    def send(self, request: Request) -> Response:
        return asyncio.run(self.send_async(request=request))

    async def send_async(self, request: Request) -> Response:
        return await self.backend.receive(request=request)
