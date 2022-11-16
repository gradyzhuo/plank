from __future__ import annotations

import inspect
from typing import List, Dict, Any, Optional, Union, TYPE_CHECKING, NoReturn

from pydantic import BaseModel

from plank.app.context import Context
from plank.serving import Serving

if TYPE_CHECKING:
    from plank.server.action.wrapper import WrapperAction
    from plank.plugin import Plugin


class Service(Serving):
    @classmethod
    def from_name(cls, name: str, plugin: Optional[Union[str, Plugin]] = None) -> Service:
        context = Context.standard(namespace=Serving.__qualname__)
        if plugin is not None:
            plugin_name = plugin.name if isinstance(plugin, Plugin) else plugin
            name = f"{plugin_name}.{name}"
        return context.get(key=name)

    @classmethod
    def register(cls, serving: Serving, name: Optional[str] = None,
                 plugin: Optional[Union[str, Plugin]] = None) -> NoReturn:
        name = name or serving.name() or id(serving)
        name = name if plugin is None else f"{plugin}.{name}"
        context = Context.standard(namespace=Serving.__qualname__)
        context.set(key=name, value=serving)

    @classmethod
    def registered(cls, plugin: Optional[Union[str, Plugin]] = None) -> List[Service]:
        plugin = plugin or ""
        context = Context.standard(namespace=Serving.__qualname__)
        return [
            service
            for key, service in context.items()
            if key.startswith(plugin)
        ]

    def in_plugin(self) -> Plugin:
        assert self.__plugin is not None, "The property of service should be set when did `add_service` to a plugin."
        return self.__plugin

    def __init__(self, name: Optional[str] = None, serving_path: Optional[str] = None, plugin: Optional[Plugin] = None):
        self.__name = name
        self.__serving_path = serving_path
        self.__plugin = plugin

    def name(self) -> str:
        return self.__name

    def serving_path(self) -> Optional[str]:
        return None if self.__serving_path is None else Context.standard().reword(self.__serving_path)

    def perform(self, arguments: BaseModel) -> Any:
        raise NotImplementedError()

    def get_actions(self) -> Dict[str, WrapperAction]:
        from plank.server.action.wrapper import WrapperAction
        member_items = inspect.getmembers(self, predicate=lambda member: isinstance(member, WrapperAction))
        return dict(member_items)

    def __did_add_to_plugin__(self, plugin: Plugin):
        self.__plugin = plugin
