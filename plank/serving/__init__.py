from __future__ import annotations

from typing import Any


class Serving:
    def name(self) -> str:
        raise NotImplementedError

    def perform(self, *args, **kwargs) -> Any:
        raise NotImplementedError
