from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

import toml

from .info import ConfigInfo, ConfigInfoManager
from plank.context import Context

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
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
    @classmethod
    def default(cls) -> Configuration:
        singleton = getattr(cls, _Configuration__default_key)
        assert singleton is not None, "The singleton of Configuration not found. please perform `set_default` first."
        return singleton

    @property
    def name(self) -> str:
        return self.__name

    @property
    def context(self) -> Context:
        return self.__context

    @property
    def app(self) -> AppConfigInfo:
        return self.__config_infos["app"]

    @property
    def logger(self) -> LoggerConfigInfo:
        return self.__config_infos["logger"]

    @property
    def path(self) -> PathConfigInfo:
        return self.__config_infos["path"]

    @property
    def plugin(self) -> PluginConfigInfo:
        return self.__config_infos["plugin"]

    @property
    def service(self) -> ServiceConfigInfo:
        return self.__config_infos["service"]

    @property
    def extra(self) -> ExtraConfigInfo:
        return self.__config_infos["extra"]

    @classmethod
    def build(cls, name:str, config_dict: Dict[str, Any], context: Optional[Context]=None):
        context = context or Context.standard()
        program_dict = {}
        manager = ConfigInfoManager.default()
        for key, config_dict in config_dict.items():
            handler_type = manager.get_handler_type(namespace=key)
            if handler_type is not None:
                program_dict[key] = handler_type(namespace=key, config_dict=config_dict, context=context)

        return Configuration(name=name, context=context,
                                                config_infos=program_dict)

    def __init__(self, name: str, context: Context, config_infos: Dict[str, ConfigInfo]):
        self.__name = name
        self.__context = context
        self.__config_infos = config_infos

    def set_default(self):
        setattr(type(self), _Configuration__default_key, self)

    def config_info(self, keyspace: str) -> Optional[ConfigInfo]:
        manager = ConfigInfoManager.default()
        registed_infos = manager.registed_types()
        for key in registed_infos.keys():
            if keyspace.startswith(key):
                return self.__config_infos[key]
        # didn't match any registered infos.
        return None

    def set(self, keyspace: str, value: Optional[Any]):
        config_info = self.config_info(keyspace=keyspace)
        config_info.set(key=keyspace, value=value)

    def get(self, keyspace: str, default: Optional[Any] = None) -> Optional[Any]:
        config_info = self.config_info(keyspace=keyspace)
        return config_info.get(key=keyspace, default=default)


class ProgramPool:

    @classmethod
    def build(cls, path: Path, extra_info: Optional[Dict[str, Any]] = None) -> ProgramPool:
        toml_fp = path.open("r+")
        origin_config_dict = toml.load(toml_fp)
        toml_fp.close()

        extra_info = extra_info or {}

        flatten_config_dict = flatten_dict(origin_config_dict)

        env_prefix_key = "app.env.prefix"
        if env_prefix_key in flatten_config_dict.keys():
            env_key_prefix = flatten_config_dict[env_prefix_key]
        else:
            env_key_prefix = "PL"

        for keyspace, value in copy.copy(flatten_config_dict).items():
            env_keys = f"{env_key_prefix}_{keyspace.replace('.', '_').upper()}"
            environ_str_value = os.environ.get(env_keys)
            if environ_str_value is None:
                environ_value = value
            elif isinstance(value, (list, int, float, dict, float)):
                environ_value = json.loads(environ_str_value)
            else:
                environ_value = environ_str_value
            flatten_config_dict[keyspace] = environ_value

        flatten_dicts = {}
        for keyspace, value in flatten_config_dict.items():
            top_level_name = keyspace.split(".")[0]
            sub_dict = flatten_dicts.setdefault(top_level_name, {})
            sub_dict[keyspace] = value

        manager = ConfigInfoManager.default()
        registed_types_dict = manager.registed_types()
        for name in registed_types_dict.keys():
            flatten_dicts.setdefault(name, {})

        program_override_dicts = origin_config_dict.pop("program")
        program_override_dicts["base"] = {}
        programs = ProgramPool()
        for program_name, program_override_dict in program_override_dicts.items():
            program_context = Context(namespace=f"program.{program_name}")
            program_context.update(extra_info)

            program_config_dict = {}
            program_config_dict.update(copy.deepcopy(flatten_dicts))
            for override_key, override_config_dict in program_override_dict.items():
                override_flatten_dict = flatten_dict(override_config_dict, parent_key=override_key)
                updated_dict = program_config_dict[override_key]
                updated_dict.update(override_flatten_dict)

            configuration = Configuration.build(name=program_name, config_dict=program_config_dict, context=program_context)
            programs.add(configuration=configuration)
        return programs

    def __init__(self, defaults: Optional[List[Configuration]] = None):
        self.__configurations = {}
        default_configurations = defaults or []
        for configuration in default_configurations:
            self.add(configuration)

    def add(self, configuration: Configuration):
        self.set(program_name=configuration.name, configuration=configuration)

    def set(self, program_name: str, configuration: Configuration):
        self.__configurations[program_name] = configuration

    def get(self, program_name: str) -> Optional[Configuration]:
        return self.__configurations[program_name]

    def pop(self, program_name: str) -> Optional[Configuration]:
        return self.__configurations.pop(program_name)

    def keys(self) -> List[str]:
        return list(self.__configurations.keys())

    def __repr__(self) -> str:
        return str(self.__configurations)

