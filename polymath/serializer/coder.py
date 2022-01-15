from .abstract import ICoder
from typing import Union
import zlib

class CompressCoder(ICoder):
    enum_name = "COMPRESS"

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, new_value):
        self.__level = new_value

    def __content_type__(self):
        return "gzip/gz"

    def __extension__(self):
        return "gz"

    def __init__(self, level:int=6, proxy:Union[None, ICoder]=None): 
        super().__init__(proxy=proxy)
        self.__level = level 
        
    def __encode__(self, value:bytes)->bytes:
        return zlib.compress(value, level=self.level)

    def __decode__(self, data:bytes)->bytes:
        return zlib.decompress(data)

    def __represent__(self)->dict:
        return {
            "level": self.__level
        }