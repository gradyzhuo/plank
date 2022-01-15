from __future__ import annotations
from polymath.plugins import Plugin
from polymath.plugins.manager import PluginManager
from polymath.plugins.resource import Resource
from polymath.config import Configuration
from polymath.serving.extension import Extension, ExtensionInfo
from typing import Optional, List, Any, Generator, Union, Dict, Type
from pathlib import Path
from functools import reduce

_Application__singleton_key = "__sigleton"

class ApplicationDelegate:
        def application_will_launch(self, app:Application, launch_options: Dict[str, Any]): pass
        def application_did_launch(self, app:Application): pass
        def application_discover_plugin_prefix(self, app: Application)->str:
            return f"{app.name}_plugin_"
        def application_did_discover_plugins(self, app: Application, plugins:List[Plugin]): pass
        def application_should_load_plugin(self, app: Application, plugin:Plugin)->bool: return True


class Application:

    @classmethod
    def set_default_delegate_type(cls, delegate_type: Type[ApplicationDelegate]):
        assert issubclass(delegate_type, ApplicationDelegate) , f"{delegate_type} should be inherited from ApplicationDelegate."
        cls.Delegate = delegate_type

    @property
    def name(self)->str:
        return self.__name

    @property
    def version(self)->str:
        return self.__version

    # @property
    # def mode(self)->str:
    #     return self.configuration.mode_name

    @property
    def workspace(self)->Path:
        return self.__workspace

    # @property
    # def debug_mode(self)->bool:
    #     return self.configuration.debug_mode
    #
    # @property
    # def configuration(self)->Configuration:
    #     return self.__configuration

    @property
    def delegate(self)->ApplicationDelegate:
        return self.__delegate

    @property
    def plugins(self)->List[Plugin]:
        return self.__plugin_manager.plugins

    @property
    def loaded(self):
        return self.__loaded

    @property
    def launch_options(self)->Dict[str, str]:
        return self.__launch_options or {}

    @classmethod
    def main(cls)->Application:
        if not hasattr(cls, _Application__singleton_key):
            raise RuntimeError(f"Application had no an instance. please get instance by Application(delegate=...) first.")
        return getattr(cls, _Application__singleton_key)
    
    def __init__(self, name: str, version: str, delegate: ApplicationDelegate) -> None:
        self.__name = name
        self.__version = version
        self.__plugin_manager: PluginManager = PluginManager.default()
        self.__delegate = delegate
        self.__loaded = False
        self.__launch_options = None

        # self.__configuration = configuration

        if not hasattr(Application, _Application__singleton_key):
            self.as_main()


    def as_main(self):
        setattr(Application, _Application__singleton_key, self)
        

    def find_extensions(self, name:Optional[str]=None, extension_type: Optional[Type[Extension]]=None)->Generator[ExtensionInfo, None, None]:
        extension_infos = reduce(lambda results, plugin: results + plugin.extensions(type=extension_type), self.__plugin_manager.plugins, [])
        return filter(lambda extension_info: (extension_info.name == name) ^ (name is None), extension_infos)

    def extension_info(self, name: str, by_type: Type[Extension]) -> Optional[ExtensionInfo]:
        extension_infos = self.find_extensions(name=name, extension_type=by_type)
        try:
            return next(extension_infos)
        except:
            return None

    def extension(self, name:str, by_type: Type[Extension])->Optional[Extension]:
        extension_info = self.extension_info(name=name, by_type=by_type)
        return extension_info.extension if extension_info is not None else None

    def plugin(self, name:str)->Plugin:
        return self.__plugin_manager.get_plugin(name)

    def resource(self, resource_name: str, in_plugin: Union[str, Plugin]) -> Optional[Resource]:
        in_plugin = in_plugin if isinstance(in_plugin, Plugin) else self.plugin(in_plugin)
        if in_plugin is not None:
            return in_plugin.shared_resources.get(resource_name)

    def load(self, workspace: Path, configuration_path: Path, launch_options: Optional[Dict[str, Any]]=None):
        if self.__loaded:
            return

        # config_name = config_name or "debug"

        # configuration_path = workspace / "configuration" / f"{config_name}.yml"
        configuration = Configuration.from_file(file_path=configuration_path)
        configuration.add_path("workspace", workspace)
        configuration.set_default()

        launch_options = launch_options or self.launch_options
        configuration.reload(extra=launch_options)
        self.__loaded = True

        plugin_prefix = self.delegate.application_discover_plugin_prefix(app=self)
        plugins = self.__plugin_manager.discover(plugin_prefix=plugin_prefix, install=True)
        if len(plugins) > 0:
            self.delegate.application_did_discover_plugins(app=self, plugins=plugins)

        for plugin in self.plugins:
            if self.delegate.application_should_load_plugin(app=self, plugin=plugin):
                plugin.load()

    def unload(self):
        for plugin in self.plugins:
            plugin.unload()
        self.__loaded = False

    def launch(self, workspace: Path, configuration_path: Path, **options):
        self.__launch_options = options
        self.__delegate.application_will_launch(self, options)
        self.load(workspace=workspace, configuration_path=configuration_path,launch_options=options)
        self.__delegate.application_did_launch(self)

    def did_set_launcher(self, launcher):
        pass


