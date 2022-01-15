from polymath.config.attribute import Attribute
from typing import List, Optional, Dict
import toml

config = {
    'app': {
            'name': 'Undefined',
            'version': '0.0.1',
            'DEBUG': True,
            'context': {
                'logger': {
                        'level': {
                            'env': 'APPLICATION_LOGGER_LEVEL',
                            'default': 'DEBUG'
                        }
                },
                'path': {
                    'workspace': {
                        'env': 'APPLICATION_WORKSPACE',
                        'default': '/var/aiteam/app/${app.name}'
                    },
                    'data': {
                        'env': 'APPLICATION_DATA_FOLDER',
                        'default': '$workspace/data'
                    }
                }
            }
    }
}

class ContextConfig:

    @property
    def attributes(self)->Dict[str, Attribute]:
        return self.__attributes

    def __init__(self, namespace: str):
        self.__namespace = namespace
        self.__attributes = {}

    def add(self, name: str, attribute: Attribute):
        self.attributes[name] = attribute

    def pop(self, name: str) -> Optional[Attribute]:
        return self.attributes.pop(name)

    def __getitem__(self, name: str) -> Attribute:
        return self.attributes[name].value

class Configuration:
    def __load(self):
        app_config = config["app"]
        app_name = app_config["name"]
        app_version = app_config["version"]
        app_debug = app_config["debug"]

        context_config = app_config.pop("context")

        logger_config = context_config.pop("logger")
        logger = ContextConfig(namespace="app.context.logger")
        for name, attribute_config in logger_config.items():
            logger.add(name=name, attribute=Attribute.from_dict(attribute_config))


        path_config = context_config.pop("path")
        path = ContextConfig(namespace="app.context.path")
        for name, attribute_config in path_config.items():
            path.add(name=name, attribute=Attribute.from_dict(attribute_config))






