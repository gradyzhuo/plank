from __future__ import annotations
from plank.plugin.resource import Resource
from plank.serializer import Serializer
from .dictionary import DictionaryTransferable
from typing import Optional, Any, Dict, List



class RecordsResource(Resource, DictionaryTransferable):
    @classmethod
    def type(cls) -> str:
        return "records"

    @classmethod
    def from_value(cls, value: List[Dict[str, Any]]) -> Resource:
        assert type(value) is list, f"The value of RecordsResource should be type `list`, not {value.__class__.__name__}."
        return cls.__call__(value)

    @classmethod
    def from_file(cls, fiile_path: str, mode: str, serializer: Serializer, encoding:Optional[str]=None):
        encoding = encoding or "utf8"
        with open(fiile_path, mode) as fp:
            data = fp.read().encode(encoding)
            records = serializer().deserialize(data)
            return cls.from_value(records)

    @classmethod
    def from_json_path(cls, path, mode: str, encoding:Optional[str]=None):
        return cls.from_file(path, mode, Serializer.json, encoding=encoding)

    @classmethod
    def from_pickle_path(cls, path, mode: str, encoding:Optional[str]=None):
        return cls.from_file(path, mode, Serializer.pickle, encoding=encoding)

    def __init__(self, resource_value: List[Dict[str, Any]]):
        self._resource_value = resource_value
        self._resource_dict = self.to_dict()

    def _get_(self, key):
        if type(key) is int:
            return self._resource_value[key]
        else:
            return self._resource_dict[key]

    def to_records(self)->Optional[List[Dict[str, Any]]]:
        return self._resource_value

    def to_dict(self):
        records:List[Dict[str, Any]] = self._resource_value
        dict_result = {}
        for pack in zip(*[ record.items() for record in records]):
            for key, item in pack:
                values = dict_result.setdefault(key, [])
                values.append(item)
        return dict_result

class RecordsTransferable:
    def to_records(self)->Dict[str, Any]:
        raise NotImplementedError(f"Not supported of resource type: `{type(self)}`.")