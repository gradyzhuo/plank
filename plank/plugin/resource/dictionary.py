from __future__ import annotations
from plank.plugin.resource import Resource
from typing import Any, List, Tuple, Dict

class DictionaryResource(Resource):
    @classmethod
    def type(cls) -> str:
        return "dictionary"

    @classmethod
    def from_mapping(cls, keys:List[str], values:List[Any]) -> Resource:
        return cls.from_value(dict(zip(keys, values)))

    def keys(self)->List[str]:
        return self.resource_value.keys()

    def values(self)->List[Any]:
        return self.resource_value.values()

    def items(self)->List[Tuple]:
        return self.resource_value.items()

class DictionaryTransferable:
    def to_dict(self)->Dict[str, Any]:
        raise NotImplementedError(f"Not supported of resource type: `{type(self)}`.")
