from ..info import ConfigInfo

class LoggerConfigInfo(ConfigInfo):

    @property
    def level(self)->str:
        return self.__level

    def __configure__(self):
        self.__level = self.get("level")