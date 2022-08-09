from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Any, Dict, Type, Union
from polymath import logger
from polymath.plugin import Plugin
from polymath.plugin.module import ModulePlugin
from polymath.config import Configuration
from polymath.serving.service import Service
from polymath.serving.service import ServiceManagerable
from polymath.app.context import Context

_Application__singleton_key = "__sigleton"

class Application(ServiceManagerable):
    class Delegate:
        def application_will_launch(self, app: Application, launch_options: Dict[str, Any]): pass

        def application_did_launch(self, app: Application): pass

        def application_discover_plugin_prefix(self, app: Application) -> str:
            return f"{app.name}_plugin_"

        def application_using_plugin_type(self, app: Application) -> Type[Plugin]:
            return ModulePlugin

        def application_did_discover_plugins(self, app: Application, plugins: List[Plugin]): pass

        def application_should_install_plugin(self, app: Application, plugin: Plugin) -> bool: return True

        def application_did_install_plugin(self, app: Application, plugin: Plugin): pass

        def application_should_load_plugin(self, app: Application, plugin: Plugin) -> bool: return True

        def application_did_load_plugin(self, app: Application, plugin: Plugin): pass

    @classmethod
    def set_default_delegate_type(cls, delegate_type: Type[Application.Delegate]):
        assert issubclass(delegate_type, Application.Delegate) , f"{delegate_type} should be inherited from Application.Delegate."
        cls.Delegate = delegate_type

    @property
    def name(self)->str:
        return self.__name

    @property
    def version(self)->str:
        return self.__version

    @property
    def build_version(self)->str:
        return self.__build_version

    @property
    def workspace(self)->Path:
        return self.configuration.path.workspace

    @property
    def debug(self)->bool:
        return self.configuration.app.debug

    @property
    def plugin_name_prefix(self)->str:
        return self.__plugin_name_prefix

    @property
    def configuration(self)->Configuration:
        return self.__configuration

    @property
    def delegate(self)->Application.Delegate:
        return self.__delegate

    @property
    def plugins(self)->List[Plugin]:
        plugin_type = self.delegate.application_using_plugin_type(app=self)
        return plugin_type.installed()

    @property
    def loaded(self):
        return self.__loaded

    @classmethod
    def main(cls)->Application:
        if not hasattr(cls, _Application__singleton_key):
            raise RuntimeError(f"Application had no an instance. please get instance by Application(delegate=...) first.")
        return getattr(cls, _Application__singleton_key)

    @classmethod
    def construct(cls, name:str, version: str, delegate: Union[Application.Delegate, Type[Application.Delegate]], workspace_path: Path, build_version: Optional[str]=None, configuration_path:Optional[Path]=None, **kwargs)->Application:
        defaults = Context.standard()
        defaults.set("workspace_path", str(workspace_path))
        defaults.set("application.name", name)
        defaults.set("app.name", name)

        configuration_path = configuration_path or workspace_path / "configuration" / "configuration.toml"
        Configuration.preload(path=configuration_path)
        if not isinstance(delegate, Application.Delegate) and issubclass(delegate, Application.Delegate):
            delegate = delegate()
        application = Application(name=name, version=version, build_version=build_version, delegate=delegate, **kwargs)
        if not hasattr(cls, _Application__singleton_key):
            application.as_main()
        return application

    
    def __init__(self, name:str, version: str, delegate: Application.Delegate, build_version:Optional[str]=None) -> None:
        self.__name = name
        self.__version = version
        self.__build_version = build_version or version
        self.__delegate = delegate
        self.__loaded = False
        self.__configuration: Optional[Configuration] = None
        self.__server = None
        self.__plugin_name_prefix = delegate.application_discover_plugin_prefix(app=self)


    def as_main(self):
        setattr(Application, _Application__singleton_key, self)

    def plugin(self, name:str)->Plugin:
        plugin_type = self.delegate.application_using_plugin_type(app=self)
        return plugin_type.plugin(name=name)

    def _load_plugin(self):
        plugin_type = self.delegate.application_using_plugin_type(app=self)
        plugins = plugin_type.discover(plugin_prefix=self.__plugin_name_prefix)

        if len(plugins) > 0:
            self.delegate.application_did_discover_plugins(app=self, plugins=plugins)
        for plugin in plugins:
            try:
                if self.delegate.application_should_install_plugin(app=self, plugin=plugin):
                    plugin_type.install(plugin=plugin)
                    self.delegate.application_did_install_plugin(app=self, plugin=plugin)
                if self.delegate.application_should_load_plugin(app=self, plugin=plugin):
                    plugin.load()
                    self.delegate.application_did_load_plugin(app=self, plugin=plugin)
            except Exception as e:
                logger.error(f"The error happened on loading plugin: {plugin.name}.")
                raise e

    def unload(self):
        for plugin in self.plugins:
            plugin.unload()
        self.__loaded = False

    def launch(self, program:str, **options):
        if self.__loaded: return

        assert program is not None, "The program of configuration is needed."
        self.__configuration = Configuration.from_program(program_name=program, as_default=True)
        self.__delegate.application_will_launch(self, options)
        standard_defaults = Context.standard()
        standard_defaults.update(options)
        standard_defaults.update({
            "program": program
        })
        self.__delegate.application_did_launch(self)

        self._load_plugin()
        for plugin in self.plugins:
            plugin.delegate.application_did_launch(plugin=plugin, launch_options=options)

        self.__loaded = True

    def _server_did_startup(self, server):
        for service in Service.registered():
            backends = service.get_backends()
            server.add_backends(*backends)

    def _server_did_shutdown(self, server):
        pass

