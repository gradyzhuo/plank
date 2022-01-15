from __future__ import annotations
from polymath import logger
from typing import Dict, Optional
import yaml
from polymath.config.attribute import Attribute
from pathlib import Path
import re
from .define import envs

rx = r'\$\{(?P<VAR>[a-z A-Z]{1}[\w _ 0-9]+)\}'

def replace_var(string, replaced=lambda var_name: var_name):
    def replaces(matchobj):
        VAR = matchobj.groupdict()["VAR"]
        replaced_path = replaced(VAR.lower())
        return replaced_path or f"${VAR}"
    return re.sub(rx, replaces, str(string))

_Configuration__singleton_key = "__sigleton"
class Configuration:
    context = {}

    @classmethod
    def reword(cls, var, name=None, extra_info=None):
        grounds_dict = {}
        extra_info = extra_info or {}
        grounds_dict.update(cls.context)
        grounds_dict.update(extra_info)
        result = grounds_dict.get(var) \
                 or replace_var(var, replaced=lambda var_name: grounds_dict.get(var_name, f"${var_name}"))
        if name is not None:
            cls.context[name] = result
        return result

    __default = None

    @property
    def name(self) -> str:
        return self.__name

    @property
    def info_dict(self)->Dict[str, Attribute]:
        return self.__info_dict

    @property
    def debug_mode(self):
        return self._debug_mode

    @property
    def mode_name(self)->str:
        return "debug" if self.debug_mode else "release"

    @property
    def data_folder_path(self)->Path:
        return self.path(name="data")

    @property
    def language(self)->str:
        return self.__info_dict["language"].value

    @classmethod
    def default(cls) -> Configuration:
        return getattr(cls, _Configuration__singleton_key)

    @classmethod
    def from_file(cls, file_path: Path, extra_config:Dict[str, str] = None):
        config_name = file_path.name.removesuffix(".yml")
        with file_path.open("r") as fp:
            config = yaml.load(fp, Loader=yaml.FullLoader)
        logger.info(f"Loaded configuration path: {file_path}")
        logger.info(f"configuration: {config}")
        extra_config = extra_config or {}
        for key, e_c in extra_config.items():
            if isinstance(e_c, dict):
                for _k, _v in e_c.items():
                    config[key][_k] = _v
            else:
                config[key] = e_c

        if "base" in config.keys():
            base_name = config["base"]
            del config["base"]
            return cls.from_name(base_name, extra_config=config)
        
        debug_mode = config.get("debug", False)
        info_dict = {
            key: Attribute.from_dict(config_dict=attribute_dict)
            for key, attribute_dict in config.get("info", {}).items()
            if key not in cls.context
        }
        cls.context.update({
            key: attribute.value
            for key, attribute in info_dict.items()
        })

        paths_dict = config.get("path", {})
        for name, path_dict in paths_dict.items():
            env_key = path_dict["env"]
            envs.register(env_key, default=path_dict["default"])

        envs.sync()

        raw_paths = {}
        for name, path_dict in paths_dict.items():
            env_key = path_dict["env"]
            path_value = envs[env_key]
            raw_paths[name] = path_value
            if "$" not in path_value:
                cls.context[name] = path_value

        return cls.__call__(config_name=config_name, info_dict=info_dict, raw_paths=raw_paths, debug_mode=debug_mode)

    def __init__(self, config_name: str, info_dict: Dict[str, str], raw_paths:Dict[str, str], debug_mode=False) -> None:
        self.__name = config_name
        self.__info_dict = info_dict
        self.__raw_paths = raw_paths
        self.__paths = {}
        self._debug_mode = debug_mode


    def get(self, name, default=None):
        attribute = self.info_dict.get(name)
        return attribute.value if attribute is not None else default

    def add_path(self, name:str, path: Path):
        self.__paths[name] = path
        type(self).context[name] = str(path)

    def remove_path(self, name: str)->Path:
        path = self.__paths[name]
        del self.__paths[name]
        return path

    def path(self, name: str)->Path:
        cls = type(self)
        path_str = self.__raw_paths[name]
        if name not in self.__paths.keys():
            path = Path(cls.reword(path_str, name=name))
            self.__paths[name] = path
        return self.__paths[name]

    def reload(self, extra: Optional[Dict[str, str]] = None):
        extra = extra or {}
        cls = type(self)
        cls.context.update(extra)
        for name, path_str in self.__raw_paths.items():
            cls.reword(path_str, name=name)


    def set_default(self):
        setattr(type(self), _Configuration__singleton_key, self)