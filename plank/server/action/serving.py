import inspect
from plank.serving import Serving
from plank.server.action import Action
from plank.server.message import Request, Response
from typing import Union, List, Dict, Any
from pydantic import BaseModel
from functools import reduce

class ServingAction(Action):

    @property
    def serving(self)->Serving:
        return self.__serving

    def __init__(self, path: str, serving: Serving):
        self.__path = path
        self.__serving = serving

    def routing_path(self) ->str:
        return self.__path

    async def receive(self, request: Request) -> Response:
        # request.arguments

        sig = inspect.signature(self.serving.perform)
        parameter_names = sig.parameters.keys()

        def handle(args: Union[List[Any], Dict[str, Any]], parameter: inspect.Parameter):
            arg = args[parameter.name]
            if isinstance(arg, dict) and issubclass(parameter.annotation, BaseModel):
                return parameter.annotation.construct(**arg)
            else:
                return arg

        # for name, parameter in sig.parameters.items():
        #     print(parameter.annotation, isinstance(body, parameter.annotation))

        if len(parameter_names) == 1:
            parameter_name = list(parameter_names)[0]
            parameter = sig.parameters[parameter_name]
            if issubclass(parameter.annotation, BaseModel):
                if isinstance(request.arguments, dict):
                    argument_count = len(request.arguments.keys())
                    model_keys = parameter.annotation.schema(by_alias=True).keys()
                    if argument_count > 0:
                        keys_compared = reduce(lambda result, item: result and (item in model_keys), request.arguments.keys(), True)
                        if keys_compared:
                            model = parameter.annotation.construct(**request.arguments)
                        else:
                            model = parameter.annotation.construct(**request.arguments[parameter_name])
                    else:
                        model = parameter.annotation.construct()
                    response_value = self.serving.perform(model)
                else:
                    model = parameter.annotation.construct(**request.arguments)
                    response_value = self.serving.perform(model)
            else:
                response_value = self.serving.perform(**request.arguments)
        else:
            pass_arguments = {
                name: handle(request.arguments, parameter)
                for name, parameter in sig.parameters.items()
            }
            response_value = self.serving.perform(**pass_arguments)

        if inspect.isawaitable(response_value):
            response_value = await response_value
        return Response(value=response_value)
