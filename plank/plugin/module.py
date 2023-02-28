from __future__ import annotations

import asyncio
import importlib
import inspect
import pkgutil
import traceback
import sys
from pathlib import Path
from typing import NoReturn, Dict, Any, Optional, List, Type, Union

import nest_asyncio
from plank import logger
from plank.context import Context
from plank.configuration import Configuration
from plank.plugin import Plugin
from plank.plugin.asset import Asset

nest_asyncio.apply()

class ModulePlugin(Plugin):
    __package_name_mappings__: Dict[str, Plugin] = {}
    __available_prefix__: List[str] = []

    class PluginContext(Context):
        def store(self, value: Any, for_key: str):
            return self.set(key=for_key, value=value)

        def get_value(self, for_key: str) -> Optional[Any]:
            return self.get(key=for_key, reword=True)

        def __getitem__(self, key: str):
            return self.get_value(for_key=key)

    @classmethod
    def __discover_module(cls, plugin_prefix: str, paths: Optional[List[str]] = None) -> Dict[str, pkgutil.ModuleInfo]:
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules(paths)
            if name.startswith(plugin_prefix)
        }

    @classmethod
    def discover(cls, plugin_prefix: str) -> List[Plugin]:
        cls.__available_prefix__.append(plugin_prefix)
        current_path = str(Path.cwd())
        if current_path not in sys.path:
            sys.path.append(current_path)
        modules_dict = {}
        site_package_modules = cls.__discover_module(paths=None, plugin_prefix=plugin_prefix)
        current_path_modules = cls.__discover_module(paths=[current_path], plugin_prefix=plugin_prefix)
        modules_dict.update(site_package_modules)
        modules_dict.update(current_path_modules)

        plugins = [
            cls.from_module(module=module)
            for name, module in modules_dict.items()
        ]

        for plugin in plugins:
            plugin.did_discover()

        return plugins

    @classmethod
    def caller_plugin(cls, index=-1) -> Optional[Plugin]:
        currentframe = inspect.currentframe()
        getouterframes = inspect.getouterframes(currentframe, 2)
        modules = map(lambda frameinfo: inspect.getmodule(frameinfo.frame), getouterframes)
        configuration = Configuration.default()
        filtered = filter(
            lambda module: module is not None and hasattr(module, "__package__") and str(module.__package__).startswith(
                f"{configuration.plugin.prefix}_"), modules
        )

        try:
            module = next(filtered)
            return cls.plugin_by_module(module=module)
        except:
            return None

    @classmethod
    def clear_package_name(cls, package_name: str) -> str:
        return str(package_name).split(".")[0]

    @classmethod
    def plugin_by_module(cls, module) -> Plugin:
        package_name = cls.clear_package_name(module.__package__)
        return cls.__package_name_mappings__[package_name]

    @classmethod
    def plugin_by_object(cls, object: Union[Any, Type[Any]]) -> Plugin:
        package_name = cls.clear_package_name(object.__module__)
        return cls.__package_name_mappings__[package_name]

    @classmethod
    def current(cls) -> Plugin:
        return cls.caller_plugin()

    @classmethod
    def from_module(cls: Type[ModulePlugin], module):
        init_parameters = cls.construct_parameters(module.__plugin__)
        init_parameters["module"] = module
        return cls(**init_parameters)

    @classmethod
    def construct_parameters(cls, plugin_info: Dict[str, Any]) -> Dict[str, Any]:
        k_ModulePlugin__name = "name"
        k_ModulePlugin__kind = "kind"
        k_ModulePlugin__delegate = "delegate"

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

        name = plugin_info[k_ModulePlugin__name]
        kind = plugin_info.get(k_ModulePlugin__kind)

        try:
            _delegate = _gen_delegate(delegate_str=plugin_info.get(k_ModulePlugin__delegate))
        except Exception as e:
            err_type = e.__class__.__name__  # 取得錯誤的class 名稱
            info = e.args[0]  # 取得詳細內容
            detains = traceback.format_exc()  # 取得完整的tracestack
            n1, n2, n3 = sys.exc_info()  # 取得Call Stack
            lastCallStack = traceback.extract_tb(n3)[-1]  # 取得Call Stack 最近一筆的內容
            fn = lastCallStack[0]  # 取得發生事件的檔名
            lineNum = lastCallStack[1]  # 取得發生事件的行數
            funcName = lastCallStack[2]  # 取得發生事件的函數名稱
            errMesg = f"FileName: {fn}, lineNum: {lineNum}, Fun: {funcName}, reason: {info}, trace:\n {traceback.format_exc()}"
            logger.error(f"_gen_delegate failed: {errMesg}.")
            raise e

        return {
            "name": name,
            # "kind": kind,
            "delegate": _delegate
        }

    @property
    def kind(self)->Optional[str]:
        return self.__kind

    @property
    def module(self):
        return self.__module

    @property
    def package_name(self):
        return self.__class__.clear_package_name(self.module.__package__)

    @property
    def data_folder_path(self) -> Path:
        return self.__data_folder_path

    @property
    def context(self) -> ModulePlugin.PluginContext:
        return self.__context

    def __init__(self, name: str, module, kind: Optional[str]=None, delegate: Optional[Plugin.Delegate] = None) -> None:
        self.__name = name
        self.__kind = kind
        self.__module = module
        self.__delegate = delegate or Plugin.Delegate()
        self.__context = self.__class__.PluginContext.standard(namespace=f"plugin.config.{module.__package__}")
        self.__context.set(key="plugin", value=name)
        configuration = Configuration.default()
        self.__data_folder_path = configuration.path.get_path("plugin", extra_info={"PLUGIN": name})

    def _name(self) -> str:
        return self.__name

    def _delegate(self) -> Plugin.Delegate:
        return self.__delegate

    def did_unload(self) -> NoReturn: pass

    def unload(self):
        self.delegate.plugin_did_unload(plugin=self)
        self.did_unload()

    def did_install(self):
        self.__class__.__package_name_mappings__[self.package_name] = self

        cor_or_not = self.delegate.plugin_did_install(plugin=self)
        if inspect.isawaitable(cor_or_not):
            asyncio.run(cor_or_not)


    def did_discover(self):
        logger.debug(f"[Plugin] {self.name} discovered.")
        self.delegate.plugin_did_discover(plugin=self)

    def asset(self, name: str) -> Optional[Asset]:
        try:
            return self.__assets[name].copy_with_base_path(base_path=self.data_folder_path)
        except KeyError:
            available_keys = "[ " + ",".join(self.__assets.keys()) + " ]"
            raise KeyError(
                f"The asset name: {name}, not found in plugin: {self.name}, available keys: {available_keys}")
    def assets_by_type(self, asset_type: str) -> Dict[str, Asset]:
        return {
            asset_name: self.asset(asset_name)
            for asset_name, asset in self.__assets.items()
            if asset.type == asset_type
        }


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.__name})"
