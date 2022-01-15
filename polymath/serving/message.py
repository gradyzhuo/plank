from typing import Dict, Any

class Request:

    def headers(self)->Dict[str, str]:
        return self.__headers

    def header(self, key: str)->str:
        return self.headers()[key]

    def arguments(self)->Dict[str, Any]:
        return self.__arguments

    def __init__(self, arguments: Dict[str, Any], headers: Dict[str, str]):
        self.__arguments = arguments
        self.__headers = headers

class Response:

    @property
    def value(self)->Any:
        return self.__value

    def __init__(self, value: Any):
        self.__value = value