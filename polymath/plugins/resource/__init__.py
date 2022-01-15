from __future__ import annotations
from typing import Any, Dict, List

class Resource:
    @classmethod
    def type(cls) -> str:
        raise NotImplementedError

    def __getitem__(self, item_or_items):
        return self._get_(item_or_items)

    @classmethod
    def from_value(cls, value) -> Resource:
        return cls.__call__(value)

    @property
    def resource_value(self) -> Any:
        return self._resource_value

    def __init__(self, resource_value: Any):
        self._resource_value = resource_value

    def _get_(self, key):
        return self._resource_value[key]






