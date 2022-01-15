import envparse
from collections import namedtuple

class Env:
    Info = namedtuple("EnvInfo", ["default", "cast", "property_name", "description"])

    def __init__(self):
        self.__registered_vars = {}

    def register(self, var, property_name=None, cast=str, default=None, description=None):
        property_name = property_name or var
        self.__registered_vars[var] = Env.Info(default=default, cast=cast, property_name=property_name, description=description)

    def unregister(self, var):
        del self.__registered_vars[var]

    def check(self, var):
        return var in self.__registered_vars and envparse.env.str(var) != envparse.NOTSET
    
    def sync(self):
        for var, info in self.__registered_vars.items():
            property_name = info.property_name
            value = envparse.env(var, default=info.default, cast=info.cast)
            self.__dict__[var] = value
            if property_name is not None:
                self.__dict__[property_name] = value
            

    def get_info(self, var):
        return self.__registered_vars.get(var, None)

    def __setattr__(self, name, value):
        if name in ["_Env__registered_vars"]:
            self.__dict__[name] = value
            return None
        if name in self.__registered_vars:
            name = self.__registered_vars[name].property_name
        self.__dict__[name] = value
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    @property
    def represented(self):
        return { var:self.__dict__[info.property_name] for var, info in self.__registered_vars.items()}
