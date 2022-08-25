from __future__ import annotations
from typing import Callable, Optional, Type
from plank.server.action.wrapper import WrapperAction
from plank.descriptor.action import ActionDescriptor

def action(path: str, wrapper_descriptor_type: Optional[Type[ActionDescriptor]]=None, **kwargs)->Callable[[Callable], ActionDescriptor]:
    descriptor_args = {}
    descriptor_args.update(kwargs)
    descriptor_args["path"] = path
    wrapper_descriptor_type = wrapper_descriptor_type or ActionDescriptor
    def _wrapper(end_point: Callable):
        descriptor_args["end_point"] = end_point
        return wrapper_descriptor_type(**descriptor_args)
    return _wrapper
