from __future__ import annotations
import importlib
from pathlib import Path
from polymath import logger
from polymath.config import Configuration
from polymath.config.attribute import Attribute
from polymath.serving.extension import Extension, ExtensionInfo
from polymath.plugins.asset import Asset
from polymath.plugins.resource import Resource
from polymath.serving.service import Service
from typing import Type, List, Optional, Dict, Any


class PluginDelegate:
    def plugin_did_install(self, plugin: Plugin):
        pass

    def plugin_did_discover(self, plugin: Plugin):
        pass

    def plugin_did_load(self, plugin: Plugin, context: Plugin.Context):
        pass

    def plugin_did_unload(self, plugin: Plugin, context: Plugin.Context):
        pass

    def plugin_did_install_extension(self, plugin: Plugin, extension_info: ExtensionInfo):
        pass

    def extensions_in_plugin(self, plugin: Plugin) -> List[ExtensionInfo]:
        pass

    def service_in_plugin(self, plugin: Plugin)->Optional[List[Service]]:
        return None

    def index_for_resource(self, plugin: Plugin, resource: Resource) -> Optional[int]:
        raise NotImplementedError(f"index_for_resource should be implemented, cause true for should_shared_index_in_plugin with type: {type(resource)}")



k_Plugin__name = "name"
k_Plugin__delegate = "delegate"
k_Plugin__config = "config"
k_Plugin__context = "context"
k_Plugin__assets_config = "assets"
k_Plugin__required_resources = "required_resources"


class Plugin:

    class Context:
        @property
        def plugin(self)->Plugin:
            from .manager import PluginManager
            return self.__dict__.setdefault("_plugin", PluginManager.default().get_plugin(self.__plugin_name))

        def __init__(self, plugin_name:str):
            self.__plugin_name = plugin_name
            self.__plugin = None
            self.__data:Dict[str, Attribute] = {}

        def store(self, value: Any, for_key: str):
            value = value if type(value) is  Attribute else \
                Attribute(value=value, env_key=f"IRIAN_{self.__plugin_name.upper()}_{for_key.replace('-', '_').upper()}") #
            self.__data[for_key] = value

        def get_value(self, for_key: str)->Optional[Any]:
            attribute = self.__data[for_key]
            if type(attribute.value) is str:
                return Configuration.reword(attribute.value, extra_info={"plugin": self.__plugin_name})
            else:
                return attribute.value

        def keys(self)->List[str]:
            return list(self.__data.keys())

        def __getitem__(self, key: str):
            return self.get_value(for_key=key)

        def reload(self):
           for v in self.__data.values():
                v.reload()

    class RequiredResource:

        @property
        def resources(self) -> Dict[str, Resource]:
            return self._resources

        def __init__(self, config_dict: Dict[str, str]):
            self._config_dict = config_dict
            self._resources = None

        def get_resources(self):
            from polymath.app import Application
            main_app = Application.main()
            required_resources_config = self._config_dict or {}
            resources = None if len(required_resources_config) == 0 else {}
            for property_name, shared_resource_path in required_resources_config.items():
                plugin_name, resource_name = shared_resource_path.split(":")
                resources[property_name] = main_app.resource(resource_name=resource_name, in_plugin=plugin_name)
            return resources

        def __getitem__(self, item):
            return self._resources[item]

        def sync(self):
            self._resources = self.get_resources()

    @property
    def name(self)->str:
        return self.__name

    @property
    def module(self):
        return self.__module

    @property
    def package_name(self):
        return self.module.__package__

    @property
    def delegate(self)->PluginDelegate:
        return self.__delegate

    @property
    def context(self)->Context:
        return self.__context

    """
    deprecated
    """
    @property
    def config(self)->Context:
        return self.context

    @property
    def shared_resources(self)-> Dict[str, Resource]:
        return self.__shared_resources


    @property
    def required_resources(self)->Dict[str, Resource]:
        return self.__required_resources

    @property
    def is_builtin(self)->bool:
        return self.name == "__builtin__"

    @property
    def data_folder_path(self)-> Path:
        return self.__data_folder_path

    @classmethod
    def current(cls) -> Plugin:
        from .manager import PluginManager
        return PluginManager.default().caller_plugin()

    @classmethod
    def from_module(cls: Type[Plugin], module, mode:str):
        def _parse_type(description: Optional[str]):
            if description is None:
                return None
            module_str, class_str = description.split(":")
            module = importlib.import_module(module_str)
            parsed_type = module.__dict__[class_str]
            return parsed_type

        def _gen_delegate(delegate_str: Optional[str]):
            delegate_type = _parse_type(delegate_str)
            return delegate_type()

        plugin_info = module.__plugin__
        name = plugin_info[k_Plugin__name]

        # context or config
        context__dict = plugin_info.get(k_Plugin__context, None) or plugin_info.get(k_Plugin__config, {})
        context_attrs = [ (attribute_name, Attribute.from_dict(config_dict=attribute_dict)) for attribute_name, attribute_dict in context__dict.items()]


        _delegate = _gen_delegate(delegate_str=plugin_info.get(k_Plugin__delegate))

        required_resources = Plugin.RequiredResource(config_dict=plugin_info.get(k_Plugin__required_resources))

        assets_dict = plugin_info.get(k_Plugin__assets_config, {})
        assets = {
            asset_name : Asset.from_config_dict(name=asset_name, config_dict=asset_dict)
          for asset_name, asset_dict in assets_dict.items()
        }

        plugin = cls(name=name,
                     module=module,
                     delegate=_delegate,
                     required_resources=required_resources,
                     context_attrs=context_attrs,
                     assets=assets
                    )

        extension_infos = plugin.delegate.extensions_in_plugin(plugin)
        plugin.install_extensions(extension_infos=extension_infos)
        return plugin

    def __init__(self, name: str, module, required_resources: Optional[RequiredResource] = None,
                 delegate: Optional[PluginDelegate] = None, context_attrs: Optional[List[(str, Attribute)]] = None, assets:Optional[Dict[str, Asset]] = None) -> None:
        self.__name = name
        self.__module = module
        self.__extension_infos = []
        self.__delegate = delegate or PluginDelegate()
        self.__context = Plugin.Context(plugin_name=name)
        self.__shared_resources = {}
        self.__required_resources = required_resources
        self.__data_folder_path = Path() / Configuration.reword("$data/$plugin", extra_info={"plugin": name})

        context_attrs = context_attrs or []
        for attribute_name, attribute in context_attrs :
            self.__context.store(value=attribute, for_key=attribute_name)
        self.__assets = assets or {}

    def default_extension(self, type: Type[Extension]) -> ExtensionInfo:
        return next(filter(lambda info: info.default, self.extensions(type=type)))

    def extensions(self, type: Optional[Type[Extension]] = None) -> List[ExtensionInfo]:
        return list(
            filter(lambda extension_info: (isinstance(extension_info.extension, type)) ^ (type is None), self.__extension_infos))

    def install_extensions(self, extension_infos: List[ExtensionInfo]):
        extension_infos = extension_infos or []
        for extension_info in extension_infos:
            self.__extension_infos.append(extension_info)
            extension_info.did_install(plugin=self)
            self.__delegate.plugin_did_install_extension(plugin=self, extension_info=extension_info)

    def load(self):
        logger.info(f"plugin did load: {self.name}")

        if self.__required_resources is not None:
            self.__required_resources.sync()

        self.delegate.plugin_did_load(plugin=self, context=self.context)

    def unload(self):
        self.delegate.plugin_did_unload(plugin=self, context=self.context)


    def did_install(self):
        logger.info(f"plugin did install: {self.name}")
        self.delegate.plugin_did_install(plugin=self)

    def did_discover(self):
        logger.info(f"plugin did discover: {self.name}")
        self.delegate.plugin_did_discover(plugin=self)

    def share_resource(self, resource: Resource, for_key: str):
        self.__shared_resources[for_key] = resource

    def asset(self, name: str)->Optional[Asset]:
        try:
            return self.__assets[name].copy_with_base_path(base_path=self.data_folder_path)
        except KeyError:
            available_keys = "[ " + ",".join(self.__assets.keys()) + " ]"
            raise KeyError(f"The asset name: {name}, not found in plugin: {self.name}, available keys: {available_keys}")


    def assets_by_type(self, asset_type: str)->Dict[str, Asset]:
        return {
            asset_name: self.asset(asset_name)
            for asset_name, asset in self.__assets.items()
            if asset.type == asset_type
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.__name}, extensions={self.__extension_infos})"


