from plank.config.info import ConfigInfo

class AppConfig(ConfigInfo):

    @property
    def debug(self)->bool:
        return self.__debug

    def __configure__(self):
        self.__debug = self.get('debug')