from plank.config.info import ConfigInfo
from plank.app.context import Context
from pathlib import Path
from typing import Union, Optional, Any, Dict

class PathConfig(ConfigInfo):

    @property
    def workspace(self)->Path:
        return self.__workspace

    def get_path(self, name: str, extra_info: Optional[Dict[str, Any]]=None) -> Path:
        path = self.get(name, reword=True)
        extra_info = extra_info or {}
        extra_info.update(Context.standard().items())
        reworded_path = self.context.reword(path, extra_info=extra_info)
        return Path(reworded_path)

    def __getitem__(self, name: str)->Path:
        return self.get_path(name=name)

    def set_path(self, name: str, path: Union[str, Path]):
        self.set(name, str(path))

    def remove_path(self, name: str):
        paths = self.get("path")
        del paths[name]
        self.context.remove(key=f"{self.namespace}.path.{name}")

    def __configure__(self):
        self.__workspace = self.get("workspace")