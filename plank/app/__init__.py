from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type, TYPE_CHECKING, List

from plank.configuration import Configuration
from plank.context import Context

from plank import logger

if TYPE_CHECKING:
    from plank.plugin import Plugin
    from plank.service import ServiceManager

_Application__singleton_key = "__sigleton"


class Application:
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
        assert issubclass(delegate_type,
                          Application.Delegate), f"{delegate_type} should be inherited from Application.Delegate."
        cls.Delegate = delegate_type

    @property
    def name(self) -> str:
        return self.__configuration.app.name

    @property
    def version(self) -> str:
        return self.configuration.app.version

    @property
    def build_version(self) -> str:
        return self.configuration.app.build_version

    @property
    def workspace(self) -> Path:
        return self.configuration.path.workspace

    @property
    def debug(self) -> bool:
        return self.configuration.app.debug

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    @property
    def delegate(self) -> Application.Delegate:
        return self.__delegate

    @property
    def plugins(self) -> List[Plugin]:
        return self.__installed_plugins_context.values()

    @property
    def services(self) -> ServiceManager:
        from plank.service import ServiceManager
        return ServiceManager.shared()

    @property
    def loaded(self):
        return self.__loaded

    @classmethod
    def main(cls) -> Application:
        if not hasattr(cls, _Application__singleton_key):
            raise RuntimeError(
                f"Application had no an instance. please get instance by Application(delegate=...) first.")
        return getattr(cls, _Application__singleton_key)

    def __init__(self, delegate: Application.Delegate, configuration: Configuration) -> None:
        self.__delegate = delegate
        self.__configuration = configuration
        self.__loaded = False
        self.__installed_plugins_context = Context.standard(namespace="collection.plugins")

    def as_main(self):
        setattr(Application, _Application__singleton_key, self)

    def __processing_plugin(self):
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
                    plugin.install(context=self.__installed_plugins_context)
                    self.delegate.application_did_install_plugin(app=self, plugin=plugin)
                    # load plugin if installed, otherwise passing.
                    if self.delegate.application_should_load_plugin(app=self, plugin=plugin):
                        plugin.load()
                        self.delegate.application_did_load_plugin(app=self, plugin=plugin)
                    # add service from plugin to app
                    for name, service in plugin.services.items():
                        service.did_install(plugin=plugin)
                        self.services.add(service=service, name=name)

            except Exception as e:
                logger.error(f"[Application] The error happened on processing plugin: {plugin.name}.")
                raise e

    def plugin(self, name: str) -> Plugin:
        return self.__installed_plugins_context.get(name)

    def unload(self):
        for plugin in self.plugins:
            plugin.unload()
        self.__loaded = False

    def launch(self, **options):
        if self.__loaded:
            return
        self.__configuration.set_default()
        self.__delegate.application_will_launch(self, options)
        standard_context = Context.standard()
        standard_context.update(options)
        standard_context.update(self.configuration.context)
        self.as_main()
        self.__delegate.application_did_launch(self)

        self.__processing_plugin()
        for plugin in self.plugins:
            plugin.delegate.application_did_launch(plugin=plugin, launch_options=options)

        self.__loaded = True

    def _server_did_startup(self, server):
        pass

    def _server_did_shutdown(self, server):
        pass
