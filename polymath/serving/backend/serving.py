from polymath.serving import Serving
from polymath.serving.backend import Backend
from polymath.serving.message import Request, Response

class ServingBackend(Backend):

    def __init__(self, serving: Serving):
        self.__serving = serving

    def receive(self, request: Request) -> Response:
        arguments = request.arguments()
        response_value = self.__serving.perform(arguments=arguments)
        return Response(value=response_value)
