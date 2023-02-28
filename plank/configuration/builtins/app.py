from ..info import ConfigInfo

class AppConfigInfo(ConfigInfo):

    @property
    def debug(self)->bool:
        return self.get('debug')

    @property
    def name(self)->str:
        return self.get("name")

    @property
    def version(self)->str:
        return self.get("version")

    @property
    def build_version(self)->str:
        return self.get("build_version")

    @property
    def delegate(self)->str:
        return self.get("delegate")



