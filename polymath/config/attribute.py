from typing import Any, Optional
import json
import os

class Attribute:
    @property
    def value(self)->str:
        return self.__value

    @property
    def env_key(self)->Optional[str]:
        return self.__env_key

    @classmethod
    def from_dict(cls, config_dict):
        env_key = config_dict.get("env")
        value = config_dict.get("value", config_dict.get("default"))
        return cls(value=value, env_key=env_key)

    def __init__(self, value: Any, env_key: Optional[str]=None):
        self.__raw_value = value
        self.__value = value if env_key is None else os.environ.get(env_key, value)
        self.__env_key = env_key

    def string(self)->str:
        return str(self.value)

    def float(self)->float:
        return float(self.value)

    def int(self)->int:
        return int(self.value)

    def json(self)->Any:
        return json.loads(self.value)