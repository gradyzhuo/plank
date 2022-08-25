from __future__ import annotations
from copy import copy
from typing import Type, Callable, Dict, Any, TYPE_CHECKING
from plank.server.action.wrapper import WrapperAction
from plank.serving.service import Service
from plank.utils.path import clearify

if TYPE_CHECKING:
    from plank.server.action import Action

class ActionDescriptor:

    def __init__(self,
                 path: str,
                 end_point: Callable,
                 **kwargs
                 ):
        self.__path = path
        self.__action_args = kwargs
        self.__unbound_end_point = end_point
        self.__actions = {}

    def __get__(self, instance:Service, owner:Type[Service])->WrapperAction:
        key = id(instance)
        if key not in self.__actions.keys():
            action = self.make_action(instance, owner)
            self.__actions[key] = action
        return self.__actions[key]

    def end_point(self, instance:Service, owner:Type[Service])->Callable:
        return self.__unbound_end_point.__get__(instance, owner)

    def serving_path(self, instance:Service, owner:Type[Service]):
        instance_serving_path = instance.serving_path()
        if instance_serving_path is not None:
            path = f"/{clearify(instance.serving_path())}/{clearify(self.__path)}"
        else:
            path = f"/{clearify(self.__path)}"
        return path

    def action_extra_args(self, **init_args)->Dict[str, Any]:
        return copy(init_args)

    def make_action(self, instance:Service, owner:Type[Service])->Action:
        end_point = self.end_point(instance=instance, owner=owner)
        path = self.serving_path(instance=instance, owner=owner)
        return WrapperAction(path=path, end_point=end_point, descriptor=self)