from __future__ import annotations
from typing import Optional, Dict, Any, List, Tuple
from plank.app.context import Context
from plank.config.info import ConfigInfoManager
from plank.config.info import ConfigInfo
from plank.config.info.app import AppConfig
from plank.config.info.path import PathConfig
from plank.config.info.extra import ExtraConfig
from plank.config.info.plugin import PluginConfig
from plank.config.info.logger import LoggerConfig
import copy
from pathlib import Path
import toml

__builtin_support_handlers__ = [
    ("app", AppConfig),
    ("logger", LoggerConfig),
    ("path", PathConfig),
    ("extra", ExtraConfig),
    ("plugin", PluginConfig)
]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str ='.') -> Dict[str, Any]:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

_Configuration__default_key = "__default"
class Configuration:
    __program_configurations = {}

    @classmethod
    def default(cls) -> Configuration:
        singleton = getattr(cls, _Configuration__default_key)
        assert singleton is not None, "The singleton of Configuration not found. please perform `set_default` first."
        return singleton

    @classmethod
    def from_program(cls, program_name: str, as_default: Optional[bool] = None) -> Configuration:
        configuration = cls.__program_configurations[program_name]
        as_default = as_default or False
        if as_default:
            configuration.set_default()
        return configuration

    @classmethod
    def preload(cls, path: Path, extra_info: Optional[Dict[str, Any]]=None):
        toml_fp = path.open("r+")
        config = toml.load(toml_fp)
        toml_fp.close()

        extra_info = extra_info or {}
        context = Context.standard()
        context.update(extra_info)
        manager = ConfigInfoManager.default()

        program_override_dicts = config.pop("program")

        flatten_dicts = {
            top_level_name: flatten_dict(config.get(top_level_name, {}), parent_key=top_level_name)
            for top_level_name, _ in __builtin_support_handlers__
        }

        programs = {}
        for program_name, program_override_dict in program_override_dicts.items():
            program_dict = programs.setdefault(program_name, {})

            program_config_dict = {}
            program_config_dict.update(copy.deepcopy(flatten_dicts))
            for override_key, override_config_dict in program_override_dict.items():
                override_flatten_dict = flatten_dict(override_config_dict, parent_key=override_key)
                updated_dict = program_config_dict[override_key]
                updated_dict.update(override_flatten_dict)

            for key, config_dict in program_config_dict.items():
                handler_type = manager.get_handler_type(namespace=key)
                program_dict[key] = handler_type(namespace=key, config_dict=config_dict, context=context)

            cls.__program_configurations.update({
                program_name: Configuration(program=program_name, context=context, **program_dict)
                for program_name, program_dict in programs.items()
            })

    @property
    def program(self)->str:
        return self.__program

    @property
    def context(self)->Context:
        return self.__context

    @property
    def app(self)->AppConfig:
        return self.__config_infos["app"]

    @property
    def logger(self) -> LoggerConfig:
        return self.__config_infos["logger"]

    @property
    def path(self) -> PathConfig:
        return self.__config_infos["path"]

    @property
    def plugin(self)->PluginConfig:
        return self.__config_infos["plugin"]

    @property
    def extra(self) -> ExtraConfig:
        return self.__config_infos["extra"]

    def __init__(self, program: str, context: Context, **config_infos):
        self.__program = program
        self.__context = context
        self.__config_infos = config_infos

    def set_default(self):
        setattr(type(self), _Configuration__default_key, self)

    def config(self, namespace:str)->ConfigInfo:
        return self.__config_infos[namespace]


manager = ConfigInfoManager.default()
for namespace, config_type in __builtin_support_handlers__:
    manager.register_handler_type(namespace=namespace, handler_type=config_type)