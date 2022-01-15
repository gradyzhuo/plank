from polymath.serving.message import Request, Response
from urllib.parse import urlparse, ParseResult


class Connector:

    @property
    def address(self)->str:
        return self.__url_componentS.netloc

    @property
    def path(self)->str:
        return self.__url_componentS.path

    @property
    def url_components(self)->ParseResult:
        return self.__url_componentS

    def __init__(self, url: str):
        self.__url_componentS = urlparse(url=url)

    def send(self, request: Request)->Response:
        pass