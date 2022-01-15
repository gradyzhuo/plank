from typing import *
from .abstract import ISerializer, ICoder
from copy import copy
import pickle
import json

class Serializable:
    def represented(self)->dict:
        raise NotImplementedError(f"{self.__class__.__name__} should implement `represented`.")


class JSONSerializability(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Serializable):
            return obj.represented()
        # Let the base class default method raise the TypeError
        return super().default(obj)


class ObjectSerializer(ISerializer):

    @property
    def name(self):
        return self._name or f"{type(self).__name__}_{type(self.coder).__name__}_{self.extension}"

    @property
    def filename(self)->str:
        return f"{self._filename}.{self.extension}"

    @filename.setter
    def filename(self, new_value):
        self._filename = new_value

    @property
    def coder(self):
        return self._coder

    @coder.setter
    def coder(self, new_value):
        self._coder = new_value

    @property
    def extension(self):
        return self._coder.extension if self._coder is not None else self.__extension__()

    def __init__(self, coder:Optional[ICoder]=None, name:Optional[str]=None):
        self._coder = coder
        self._name = name

    def serialize(self, value:Serializable)->bytes:
        data = self.__serialize__(value)
        if self.coder is not None:
            data = self.coder.encode(data)
        return data

    def deserialize(self, data:bytes)->Serializable:
        if self.coder is not None:
            data = self.coder.decode(data)
        return self.__deserialize__(data=data)

    def dump(self,  value: Any, path: str):
        try:
            data = self.serialize(value)
            with open(path, "wb+") as fp:
                fp.write(data)
        except Exception as e:
            print(e)
            self.__dump__(value, path)

    def load(self, path: str)->Any:
        try:
            return  self.__load__(path)
        except:
            with open(path, "rb+") as fp:
                data = fp.read()
                return self.__deserialize__(data)

    def __serialize__(self, value:object)->bytes:
        raise NotImplementedError

    def __deserialize__(self, data:bytes)->object:
        raise NotImplementedError

    def __dump__(self, value:object, path: str):
        raise NotImplementedError

    def __load__(self, path: str)->Any:
        raise NotImplementedError


    def copy_with_coder(self, coder:ICoder):
        acopy = copy(self)
        acopy._coder = coder
        return acopy

    def __content_type__(self): pass
    def __extension__(self): pass

    @property
    def represented(self):
        info = self.__represent__()
        info["name"] = self._name
        represented_dict = {
            "enum_name": self.enum_name,
            "info"     : info
        }
        if self._coder is not None:
            represented_dict["coder"] = self._coder.represented
        return represented_dict


class BytesSerializer(ObjectSerializer):
    enum_name = "BYTES"

    def __serialize__(self, value: bytes)->bytes:
        return value

    def __deserialize__(self, data: bytes)->bytes:
        return data

    def __represent__(self)->dict:
        return {
            "encoding": self._encoding
        }

class TextSerializer(ObjectSerializer):
    enum_name = "TEXT"

    def __init__(self, encoding: str="utf8", coder: ICoder=None, name: str=None):
        self._encoding = encoding
        super().__init__(coder=coder, name=name)

    def __serialize__(self, value: str)->Any:
        return value.encode(self._encoding)

    def __deserialize__(self, data: bytes)->str:
        return data.decode(self._encoding)

    def __represent__(self)->dict:
        return {
            "encoding": self._encoding
        }

class JsonSerializer(ObjectSerializer):
    enum_name = "JSON"

    def __init__(self, coder:ICoder=None, name:str=None):
        super().__init__(coder=coder, name=name)

    def __serialize__(self, value:Serializable)->bytes:
        return  json.dumps(value, cls=JSONSerializability)

    def __deserialize__(self, data:bytes)->Any:
        return json.loads(data)

    def __content_type__(self):
        return "application/json"

    def __extension__(self):
        return "json"

class PickleSerializer(ObjectSerializer):
    enum_name = "PICKLE"

    def __init__(self, coder:ICoder=None, name:str=None, **kwargs):
        super().__init__(coder=coder, name=name)
        self.__pickle_options = kwargs

    def __serialize__(self, value:Any)->bytes:
        kwargs = self.__pickle_options
        return pickle.dumps(value, **kwargs)

    def __deserialize__(self, data:bytes)->Any:
        return pickle.loads(data)

    def __content_type__(self):
        return "application/octet-stream"

    def __extension__(self):
        return "pkl"

