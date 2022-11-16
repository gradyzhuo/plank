from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Any, Dict, Type, Union, TYPE_CHECKING
from plank import logger
from plank.config import Configuration
from plank.serving.service import Service
from plank.serving.interface import ServiceManagerable
from plank.app.context import Context

if TYPE_CHECKING:
    from plank.plugin import Plugin

_Application__singleton_key = "__sigleton"

class Application(ServiceManagerable):
    class Delegate:
        def application_will_launch(self, app: Application, launch_options: Dict[str, Any]): pass

        def application_did_launch(self, app: Application): pass

        def application_using_plugin_type(self, app: Application, prefix: str) -> Type[Plugin]:
            from plank.plugin.module import ModulePlugin
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
        return self.__configuration.app.name

    @property
    def version(self)->str:
        return self.configuration.app.version

    @property
    def build_version(self)->str:
        return self.configuration.app.build_version

    @property
    def workspace(self)->Path:
        return self.configuration.path.workspace

    @property
    def debug(self)->bool:
        return self.configuration.app.debug

    @property
    def configuration(self)->Configuration:
        return self.__configuration

    @property
    def delegate(self)->Application.Delegate:
        return self.__delegate

    @property
    def plugins(self)->List[Plugin]:
        return self.__installed_plugins or []
        # plugin_type = self.delegate.application_using_plugin_type(app=self)
        # return plugin_type.installed()

    @property
    def loaded(self):
        return self.__loaded

    @classmethod
    def main(cls)->Application:
        if not hasattr(cls, _Application__singleton_key):
            raise RuntimeError(f"Application had no an instance. please get instance by Application(delegate=...) first.")
        return getattr(cls, _Application__singleton_key)

    @classmethod
    def construct(cls, name:str, version: str, delegate: Union[Application.Delegate, Type[Application.Delegate]], workspace_path: Path, build_version: Optional[str]=None, configuration_path:Optional[Path]=None,**kwargs)->Application:
        defaults = Context.standard()
        defaults.set("workspace_path", str(workspace_path))
        defaults.set("application.name", name)
        defaults.set("app.name", name)

        configuration_path = configuration_path or workspace_path / "configuration" / "configuration.toml"
        programs = Configuration.build(path=configuration_path)
        if not isinstance(delegate, Application.Delegate) and issubclass(delegate, Application.Delegate):
            delegate = delegate()
        application = Application(name=name, version=version, build_version=build_version, delegate=delegate, programs=programs)
        if not hasattr(cls, _Application__singleton_key):
            application.as_main()
        return application

    @classmethod
    def construct_from_configuration_path(cls, configuration_path: Path, delegate: Application.Delegate, **kwargs):
        programs = Configuration.build(path=configuration_path)

        application = Application(
            delegate=delegate,
            programs=programs,
            **kwargs
        )
        if not hasattr(cls, _Application__singleton_key):
            application.as_main()

        return application

    
    def __init__(self, delegate: Application.Delegate, configuration: Configuration) -> None:
        self.__delegate = delegate
        self.__configuration = configuration
        # self.__name = configuration.app.name
        # self.__version = configuration.app.version
        # self.__build_version = configuration.app.build_version
        # self.__name = name or "${app.name}"
        # self.__version = version or "${app.version}"
        # self.__build_version = build_version or "${app.build_version}"
        self.__loaded = False
        # self.__programs = programs
        self.__installed_plugins = []

    def as_main(self):
        setattr(Application, _Application__singleton_key, self)

    def _load_plugin(self):
        plugin_prefixes = self.configuration.plugin.prefix
        plugins = []
        for prefix in plugin_prefixes:
            plugin_type = self.delegate.application_using_plugin_type(self, prefix=prefix)
            if hasattr(plugin_type, "discover"):
                plugins += (plugin_type.discover(plugin_prefix=prefix) or [])

        if len(plugins) > 0:
            self.delegate.application_did_discover_plugins(app=self, plugins=plugins)
        for plugin in plugins:
            try:
                if self.delegate.application_should_install_plugin(app=self, plugin=plugin):
                    plugin_type.install(plugin=plugin)
                    self.__installed_plugins.append(plugin)
                    self.delegate.application_did_install_plugin(app=self, plugin=plugin)
                    # load plugin if installed, otherwise passing.
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

    def launch(self, **options):
        if self.__loaded: return

        # configuration = self.__programs.get(program)
        # assert configuration is not None, f"{program} not in programs({self.__programs.keys()})"
        self.__configuration.set_default()
        self.__delegate.application_will_launch(self, options)
        standard_context = Context.standard()
        standard_context.update(options)
        standard_context.update(self.configuration.context)
        self.as_main()
        self.__delegate.application_did_launch(self)

        self._load_plugin()
        for plugin in self.plugins:
            plugin.delegate.application_did_launch(plugin=plugin, launch_options=options)

        self.__loaded = True


    def _server_did_startup(self, server):
        for service in Service.registered():
            actions = service.get_actions()
            print("actions:", actions)
            server.add_actions(*(actions.values()))

    def _server_did_shutdown(self, server): pass

