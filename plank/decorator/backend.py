from __future__ import annotations
from typing import Callable, Optional, Type
from plank.server.backend.wrapper import WrapperBackend
from plank.descriptor.backend import BackendDescriptor

def backend(path: str, wrapper_descriptor_type: Optional[Type[BackendDescriptor]]=None, **kwargs)->Callable[[Callable], BackendDescriptor]:
    descriptor_args = {}
    descriptor_args.update(kwargs)
    descriptor_args["path"] = path
    wrapper_descriptor_type = wrapper_descriptor_type or BackendDescriptor
    def _wrapper(end_point: Callable):
        descriptor_args["end_point"] = end_point
        return wrapper_descriptor_type(**descriptor_args)
    return _wrapper
