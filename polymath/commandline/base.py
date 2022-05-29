import click
from typing import List, NoReturn, Dict, Any
from polymath.serving import Serving

class BaseCommand(Serving):

    def name(self) ->str:
        return self.__name

    def __init__(self, name: str):
        self.__name = name
        self._options = self.__options__() or []
        self._arguments = self.__arguments__() or []

    def make_command(self)->click.Command:
        params = self.get_params()
        return click.Command(name=self.name(), callback=self.perform, params=params)

    def perform(self, *args, **kwargs):
        context = click.get_current_context()
        param_names = [opt.name.replace("-", "_") for opt in self.get_params()]
        parameters = dict(filter(lambda item: item[0] in param_names, context.params.items()))
        handled_parameters = self.__prepare_extension__(context, parameters)
        self.__invoke__(parameters=handled_parameters)

    def __invoke__(self, parameters: Dict[str, Any]) -> NoReturn:
        pass

    def get_params(self)->List[click.Parameter]:
        return self._arguments + self._options

    #handle paramter and return extension data
    def __prepare_extension__(self, context:click.Context, parameters: Dict[str, Any])->Dict[str, Any]:
        return parameters

    # override
    def __options__(self) -> List[click.Option]:
        return []

    # override
    def __arguments__(self) -> List[click.Argument]:
        return []