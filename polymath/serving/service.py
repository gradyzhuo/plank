from polymath.serving import Serving
from polymath.serving.extension import Extension
from typing import List, Dict, Any, Type

class Service(Serving):

    @staticmethod
    def __gen_key(name: str, type: Type[Extension]) -> str:
        type_name = type.__name__
        return f"{name}:{type_name}"

    @property
    def extensions(self):
        return self.__extensions

    def __init__(self, *extension_types: List[Type[Extension]]):
        from polymath.app import Application
        app = Application.main()
        extensions = {}
        for extension_type in extension_types:
            for info in app.find_extensions(extension_type=extension_type):
                key = self.__class__.__gen_key(info.name, extension_type)
                extensions[key] = info.extension
        self.__extensions = extensions

    def extension(self, name: str, type: Type[Extension]) -> Extension:
        key = self.__gen_key(name=name, type=type)
        return self.__extensions[key]

    def perform(self, arguments: Dict[str, Any]) -> Any:
        raise NotImplementedError()

