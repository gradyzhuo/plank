from __future__ import annotations
from .coder import *
from .serializer import *
from enum import Enum
from typing import Type, Dict, Any

class Coder(Enum):
    @classmethod
    def by_dict(cls, represented_dict: Dict[str, Any]):
        enum_name = represented_dict["enum_name"]
        info = represented_dict["info"]
        proxy_dict = represented_dict.get("proxy")
        proxy = None
        if proxy_dict is not None:
            proxy = Coder.by_dict(proxy_dict)
        info.update({
            "proxy":proxy
        })
        return cls(enum_name).cls.by_dict(info)

    compress = CompressCoder

    @property
    def cls(self)->Type[ICoder]:
        return self.value

    def __call__(self, *args, **kwargs)->Type[ICoder]:
        return self.cls(*args, **kwargs)

class Serializer(Enum):
    @classmethod 
    def by_dict(cls, represented_dict:dict): 
        enum_name = represented_dict["enum_name"]
        info = represented_dict["info"]
        kind = cls(enum_name).cls.by_dict(info)
        coder_dict = represented_dict.get("coder")
        if coder_dict is not None:
            kind.coder = Serializer.Coder.by_dict(coder_dict)
        return kind

    bytes   = BytesSerializer
    text   = TextSerializer
    json   = JsonSerializer
    pickle = PickleSerializer

    @classmethod
    def by_name(cls, name: str)->Optional[ObjectSerializer]:
        if name in ["pickle", "pkl"]:
            return cls.pickle()
        if name in ["json"]:
            return cls.json()
        if name in ["bytes"]:
            return cls.bytes()
        if name in ["text", "txt"]:
            return cls.text()
        if name in ["npz"]:
            return cls.npz()

    @property
    def cls(self)->Type[ObjectSerializer]:
        return self.value

    def __call__(self, *args, **kwargs)->Type[ObjectSerializer]:
        return self.cls(*args, **kwargs)


Serializer.Coder = Coder
