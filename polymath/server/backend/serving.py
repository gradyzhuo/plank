import inspect

from polymath.serving import Serving
from polymath.server.backend import Backend
from polymath.server.message import Request, Response
from typing import Union, List, Dict, Any
from pydantic import BaseModel
from functools import reduce

# import types
#
# def t(): pass
# argcount = 2
# co_posonlyargcount = t.__code__.co_posonlyargcount
# co_kwonlyargcount = t.__code__.co_kwonlyargcount
# co_nlocals = t.__code__.co_nlocals
# co_stacksize = t.__code__.co_stacksize
# co_flags = t.__code__.co_flags
# co_code = t.__code__.co_code
# co_consts = t.__code__.co_consts
# co_names = t.__code__.co_names
# co_varnames = t.__code__.co_varnames
# co_filename = t.__code__.co_filename
# co_name = t.__code__.co_name
# co_firstlineno = t.__code__.co_firstlineno
# co_lnotab = t.__code__.co_lnotab
# co_freevars = t.__code__.co_freevars
# co_cellvars = t.__code__.co_cellvars
#
#
# c = types.CodeType(
#     argcount,
#     co_posonlyargcount,
#     co_kwonlyargcount,
#     co_nlocals,
#     co_stacksize,
#     co_flags,
#     co_code,
#     co_consts,
#     co_names,
#     co_varnames,
#     co_filename,
#     co_name,
#     co_firstlineno,
#     co_lnotab,
#     co_freevars,
#     co_cellvars
# )
# func = types.FunctionType(code=c, name="hello", argdefs=(str, ))
# types.FunctionType()
#
#

class ServingBackend(Backend):

    @property
    def serving(self)->Serving:
        return self.__serving

    def __init__(self, path: str, serving: Serving):
        self.__path = path
        self.__serving = serving

    def path(self) ->str:
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
            print("parameter.annotation:", parameter.annotation, issubclass(parameter.annotation, BaseModel))
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
                    print("2")
                    model = parameter.annotation.construct(**request.arguments)
                    response_value = self.serving.perform(model)
            else:
                print("3")
                response_value = self.serving.perform(**request.arguments)
        else:
            print("4")
            pass_arguments = {
                name: handle(request.arguments, parameter)
                for name, parameter in sig.parameters.items()
            }
            response_value = self.serving.perform(**pass_arguments)

        if inspect.isawaitable(response_value):
            response_value = await response_value
        return Response(value=response_value)
