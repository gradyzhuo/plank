from typing import Dict, Any, Optional
from pydantic import BaseModel

class Request(BaseModel):
    headers: Dict[str, str] = {}
    arguments: Dict[str, Any]

    def header(self, key: str, default: Optional[str]=None)->Optional[str]:
        return self.headers.get(key, default)


class Response(BaseModel):
    value: Any