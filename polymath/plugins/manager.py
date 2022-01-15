from __future__ import annotations
import importlib
import pkgutil
import inspect
import sys
from polymath import logger
from polymath.config import Configuration
from polymath.plugins.asset import *
from polymath.plugins import Plugin

_PluginManager__singleton_key = "_singleton"
class PluginManager:

    @classmethod
    def default(cls) -> PluginManager:
        if not hasattr(cls, _PluginManager__singleton_key):
            instance = cls()
            setattr(cls, _PluginManager__singleton_key, instance)
        return getattr(cls, _PluginManager__singleton_key)

    @property
    def plugins(self) -> List[Plugin]:
        return list(self.__plugins.values())

    def __init__(self) -> None:
        self.__plugins = {}

    def install(self, *plugins:List[Plugin]):
        for plugin in plugins:
            self.__plugins[plugin.module.__package__] = plugin
            plugin.did_install()

    # plugin discovering in local
    def _discover_module(self, plugin_prefix:str, paths:Optional[List[str]]=None)->Dict[str, "module"]:
        plugin_prefix = plugin_prefix or Configuration.default()
        return {
            name:importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules(paths)
            if name.startswith(plugin_prefix)
        }

    def discover(self, plugin_prefix:str, install:bool=False, **kwargs)->List[Plugin]:
        mode = Configuration.default().mode_name

        current_path = str(pathlib.Path().cwd())
        if current_path not in sys.path:
            sys.path.append(current_path)

        modules_dict = {}
        site_package_modules = self._discover_module(paths=None, plugin_prefix=plugin_prefix)
        current_path_modules = self._discover_module(paths=[current_path], plugin_prefix=plugin_prefix)
        modules_dict.update(site_package_modules)
        modules_dict.update(current_path_modules)

        plugins_dict = {
            name: Plugin.from_module(module=module, mode=mode)
            for name, module in modules_dict.items()
        }

        plugins = list(plugins_dict.values())
        for plugin in plugins:
            try:
                plugin.did_discover()
            except:
                logger.warn("If you need to do preload in plugin_did_discover, using plugin_did_load instead.")
        if install:
            self.install(*plugins)

        return plugins


    def caller_plugin(self, index=-1) -> Optional[Plugin]:
        currentframe = inspect.currentframe()
        getouterframes = inspect.getouterframes(currentframe, 2)
        modules = map(lambda frameinfo: inspect.getmodule(frameinfo.frame), getouterframes)
        filtered = list(filter(
            lambda module: module is not None and hasattr(module, "__package__") and str(module.__package__).startswith(
                "irian_plugin_"), modules))
        module_namespace = filtered[0].__package__ if len(filtered) > 0 else "__main__"
        module_name = str(module_namespace).split(".")[0]
        return self.__plugins.get(module_name)

    def get_plugin(self, plugin_name) -> Plugin:
        try:
            return next(filter(lambda plugin: plugin.name == plugin_name, self.__plugins.values()))
        except:
            return None

    def __getitem__(self, package_name) -> Plugin:
        return self.__plugins[package_name]