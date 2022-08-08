from __future__ import annotations
from polymath.app.context import Context
from polymath.serving.service import Service
from typing import List, Dict, Any, NoReturn, Optional

class Plugin:
    """
    Abstract class to define what should be implemented.
    """
    __inherited__:List[Plugin] = []

    class Delegate:
        def application_did_launch(self, plugin: Plugin, launch_options: Dict[str, Any]):
            pass

        def plugin_did_install(self, plugin: Plugin):
            pass

        def plugin_did_discover(self, plugin: Plugin):
            pass

        def plugin_did_load(self, plugin: Plugin):
            pass

        def plugin_did_unload(self, plugin: Plugin):
            pass


    @classmethod
    def discover(cls, *args, **kwargs) -> List[Plugin]:
        raise NotImplementedError(f"The name of Plugin({cls.__name__}) did not implement.")

    @classmethod
    def construct_parameters(cls, plugin_info: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError(f"The construct_parameters method of Plugin({cls.__name__}) did not implement.")

    @classmethod
    def install(cls, plugin: Plugin):
        context = Context.standard(cls.__qualname__)
        context.set(key=plugin._name(), value=plugin)
        if cls is not Plugin:
            Plugin.install(plugin)
        plugin.did_install()

    @classmethod
    def installed(cls) ->List[Plugin]:
        context = Context.standard(cls.__qualname__)
        return list(context.values())

    @classmethod
    def plugin(cls, name: str)->Plugin:
        context = Context.standard(cls.__qualname__)
        if name not in context.keys():
            raise KeyError(f"Any plugin can be found with name: {name}, by type of plugin: {cls.__qualname__}.")
        return context.get(key=name)

    @classmethod
    def current(cls)->Optional[Plugin]:
        for subclass in Plugin.__inherited__:
            plugin = subclass.current()
            if plugin is not None:
                return plugin
        return None

    def __init_subclass__(cls, **kwargs):
        if cls not in Plugin.__inherited__:
            Plugin.__inherited__.append(cls)


    @property
    def name(self)->str:
        return self._name()

    @property
    def delegate(self)->Plugin.Delegate:
        return self._delegate()


    def _name(self)->str:
        raise NotImplementedError(f"The name of Plugin({self.__class__.__name__}) not implemented.")

    def _delegate(self)->Plugin.Delegate:
        raise NotImplementedError(f"The delegate of Plugin({self.__class__.__name__}) not implemented.")


    def add_service(self, service: Service):
        raise NotImplementedError(f"The method `add_service` of Plugin {self.__class__.__name__} did not implement.")

    def add_services(self, *services: Service):
        for service in services:
            self.add_service(service)

    def load(self)->NoReturn:
        pass

    def unload(self):
        pass

    def did_install(self):
        pass

    def did_discover(self):
        pass

    def services(self)->List[Service]:
        raise NotImplementedError(f"The name of Plugin({self.__class__.__name__}) not implemented.")