from __future__ import annotations
import pathlib
from enum import Enum
from pathlib import Path
from typing import *
# from polymath.serializer import Serializer
from copy import copy

class Asset:

    """
    "graph.pkl":{
            "type": "weight",
            "filename": "graph.pkl",
            "format": "pickle"
        }
    """
    class Config:
        __slots__ = ("_name", "_type", "_filename", "_format")

        @property
        def name(self) -> str:
            return self._name

        @property
        def type(self)->str:
            return self._type

        @property
        def filename(self)->str:
            return self._filename

        @property
        def format(self)->str:
            return self._format

        @classmethod
        def from_dict(cls, config_dict:Dict[str, str]):
            _name = config_dict["name"]
            _type = config_dict["type"]
            _filename = config_dict["filename"]
            _format = config_dict["format"]
            return cls(name=_name, type=_type, filename=_filename, format=_format)

        def __init__(self, name: str, type:str,  filename: str, format: str):
            self._name = name
            self._type = type
            self._filename = filename
            self._format = format


    @classmethod
    def from_config(cls, config: Config):
        _name = config.name
        _type    = config.type
        _filename = config.filename
        _format = config.format
        return cls(name=_name, type=_type, filename=_filename, format=_format)

    @classmethod
    def from_config_dict(cls, name:str, config_dict: Dict[str, str]):
        config_dict["name"] = name
        config = Asset.Config.from_dict(config_dict=config_dict)
        return cls.from_config(config=config)

    @property
    def name(self)->str:
        return self.__name

    @property
    def type(self)->str:
        return self.__type

    @property
    def filename(self)->str:
        return self.__filename

    @property
    def format(self)->str:
        return self.__format

    @property
    def base_path(self)->pathlib.Path:
        return self.__base_path

    @base_path.setter
    def base_path(self, new_value: Union[str, pathlib.Path]):
        self.__base_path = pathlib.Path() / new_value

    @property
    def folder_path(self)->pathlib.Path:
        return self.base_path / self.type

    @property
    def path(self)->pathlib.Path:
        self.folder_path.mkdir(parents=True, exist_ok=True)
        return self.folder_path / self.filename

    def __init__(self, name: str, type:str, filename: str, format:str):
        self.__name = name
        self.__type = type
        self.__filename = filename
        self.__format = format
        self.__base_path = None

    def export(self, value: Any):
        # serailizer = Serializer.by_name(self.format)
        serailizer.dump(value=value, path=self.path)

    def get_value(self)->Any:
        # serailizer = Serializer.by_name(self.format)
        return serailizer.load(self.path)

    # def path(self, base_path: Optional[Union[str, pathlib.Path]]=None, mkdir:bool=False)->pathlib.Path:
    #     from polymath.plugin import Plugin
    #     plugin = Plugin.current()
    #     if base_path is not None:
    #         base_path = pathlib.Path() / base_path
    #     elif plugin is not None:
    #         base_path = plugin.data_folder_path
    #     else:
    #         from polymath.app import Application
    #         app = Application.main()
    #         base_path = app.configuration.paths["data"]
    #     folder_path = pathlib.Path() / base_path / self.type.folder
    #     if mkdir:
    #         folder_path.mkdir(parents=True, exist_ok=True)
    #     return folder_path / self.filename

    def copy_with_base_path(self, base_path: Union[str, pathlib.Path]) -> Asset:
        copied_asset = copy(self)
        copied_asset.base_path = base_path
        return copied_asset