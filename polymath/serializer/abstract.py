class ISerializer:
    enum_name = None

    @property
    def content_type(self):
        return self.__content_type__()

    @property
    def extension(self):
        return self.__extension__()

    def __content_type__(self): pass
    def __extension__(self)->str: pass
    def __represent__(self)->dict: 
        return {}

class ICoder(ISerializer):

    @property
    def proxy(self):
        return self._proxy

    def encode(self, data:bytes)->bytes:
        data = self.__encode__(data)
        if self.proxy is not None:
            data = self.proxy.encode(data)
        return data

    def decode(self, data:bytes)->bytes:
        if self.proxy is not None:
            data = self.proxy.decode(data)
        return self.__decode__(data=data)

    def __encode__(self, data:bytes)->bytes:
        return data

    def __decode__(self, data:bytes)->bytes:
        return data

    def __init__(self, proxy=None): 
        self._proxy = proxy

    @property
    def represented(self):
        info = self.__represent__()
        represented_dict = {
            "enum_name": self.enum_name,
            "info"     : info
        }
        if self.proxy is not None:
            represented_dict["proxy"] = self.proxy.represented
        return represented_dict