from __future__ import annotations

import importlib
from typing import Dict, Any, Optional, Tuple, List, Iterable, Type

from ..info import ConfigInfo
from plank.context import Context

class ServiceConfig:
    class RemoteConfig:
        def __init__(self, config_dict: Dict[str, Any]):
            self.__config_dict = config_dict

        @property
        def scheme(self)->str:
            return self.__config_dict.get("scheme", "http")

        @property
        def host(self)->Optional[str]:
            return self.__config_dict.get("host")

        @property
        def port(self)->Optional[int]:
            return self.__config_dict.get("port")

        @property
        def path(self)->Optional[str]:
            return Context.standard().reword(self.__config_dict.get("path"))

        def base_url(self) -> Optional[str]:
            url = f"{self.scheme}://{self.host}"
            if self.port is not None:
                url = f"{url}:{self.port}"

            if self.path is not None:
                path = self.path
                if not path.startswith("/"):
                    path = "/" + path
                url = f"{url}{path}"
            return Context.standard().reword(url)



    def __init__(self, name: str, config_dict: Dict[str, Any]):
        self.__name = name
        self.__config_dict = config_dict
        self.__remote_config = ServiceConfig.RemoteConfig(config_dict=config_dict["remote"]) if "remote" in config_dict.keys() else None

        class_info = config_dict.get("class")
        if isinstance(class_info, str):
            namespace, cls_name = class_info.split(":")
        elif isinstance(class_info, dict):
            namespace = class_info["from"]
            cls_name = class_info["import"]
        else:
            namespace = None
            cls_name = None

        if namespace is not None and cls_name is not None:
            module = importlib.import_module(namespace)
            self.__class = getattr(module, cls_name)
        else:
            self.__class = None

    @property
    def service_name(self)->str:
        return self.__name

    @property
    def remote(self)->Optional[ServiceConfig.RemoteConfig]:
        return self.__remote_config

    @property
    def class_(self)->Optional[Type["Serving"]]:
        return self.__class

    def keys(self)->Iterable[str]:
        return self.__config_dict.keys()

    def __getitem__(self, key:str)->Any:
        return self.__config_dict[key]


class ServiceConfigInfo(ConfigInfo):

    def __configure__(self):
        self.__service_configs = {}
        collections = {}
        for namespace, value in self.config_dict.items():
            #format
            # service.{service_name}.{service_config_dict_name1}.{service_config_dict_name2}...{service_config_dict_namen}.{service_config_dict_key1} = {service_config_dict_value1}
            names = namespace.split(".")
            service_name = names[1]
            config_dict = collections.setdefault(service_name, {})
            sub_names = names[2:-1]
            if len(sub_names) > 0: #{service_config_dict_name1}.{service_config_dict_name2}...{service_config_dict_namen}
                for config_key in sub_names:
                    config_dict = config_dict.setdefault(config_key, {})
                    config_dict[names[-1]] = value
            else: #mean service.{service_name}.{service_config_dict_name1}.{service_config_dict_key1} = {service_config_dict_value1}
                config_dict[names[-1]] = value

        for service_config_name, service_config_dict in collections.items():
            self.__service_configs[service_config_name] = ServiceConfig(name=service_config_name, config_dict=service_config_dict)

    def keys(self)->List[str]:
        return list(self.__service_configs.keys())

    def exists(self, service_name:str)->bool:
        return service_name in self.__service_configs.keys()

    def items(self)->List[Tuple[str, ServiceConfig]]:
        return [ item for item in self.__service_configs.items()]

    def configs(self)->List[ServiceConfig]:
        return list(self.__service_configs.values())

    def get_config(self, service_name: str)->Optional[ServiceConfig]:
        return self.__service_configs.get(service_name)

    def __getitem__(self, key:str)->ServiceConfig:
        return self.__service_configs[key]

