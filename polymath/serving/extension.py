from typing import Optional, Dict, Any
from polymath.serving import Serving
import inspect

class Extension(Serving):

    @property
    def plugin(self) -> "Plugin":
        return self.__info.plugin

    @property
    def info(self):
        return self.__info

    def __repr__(self) -> str:
        return f"Extension(class={self.__class__.__name__})"

    # template for overriding
    def did_install(self): pass

    def perform(self, arguments: Dict[str, Any]) -> Any:
        method_name = arguments.pop("method")
        method = getattr(self, method_name)
        signature = inspect.signature(method)
        kwargs = {
            parameter_name:arguments[parameter_name]
            for parameter_name in signature.parameters
        }
        return method(**kwargs)

class ExtensionInfo:

    @property
    def name(self):
        return self.__name

    @property
    def type(self)->str:
        return self.extension.__class__

    @property
    def extension(self):
        return self.__instance

    @property
    def default(self) -> bool:
        return self.__default

    @property
    def plugin(self):
        return self.__plugin

    """
    :param self: 
    :param name:
    :param instance:
    :param default: (Optional) default is False.
    :return: No Return
    """

    def __init__(self, name, instance: Extension, default: Optional[bool] = None) -> None:
        self.__name = name
        self.__instance = instance
        instance._Extension__info = self
        self.__default = default or True

    def did_install(self, plugin):
        self.__plugin = plugin
        self.__instance.did_install()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type}, instance={self.__instance}, default={self.__default}, plugin={self.__plugin})"
