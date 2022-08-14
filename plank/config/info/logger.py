from plank.config.info import ConfigInfo

class LoggerConfig(ConfigInfo):

    @property
    def level(self)->str:
        return self.__level

    def __configure__(self):
        self.__level = self.get("level")