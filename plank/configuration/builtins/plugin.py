from ..info import ConfigInfo
from typing import List

class PluginConfigInfo(ConfigInfo):

    @property
    def prefix(self)->List[str]:
        prefix_items = self.get("prefix", [])
        if isinstance(prefix_items, str):
            prefix_items = [prefix_items]
        return [self.context.reword(str(item)) for item in prefix_items ]

    def __configure__(self):
        self.__connectors = {}
        # for namespace, value in self.config_dict.items():
        #     print("?????????, namespace:", namespace, "value:", value)
        #     rx = r'plugin\.(?P<PLUGIN_NAME>[_a-zA-Z]{1}[._\w]+)\.(?P<FEATURE>[a-z A-Z]{1}[._\w]+)\.(?P<META_KEY>[._\w]+)'
        #     match_obj = re.match(rx, namespace)
        #     plugin_name = match_obj["PLUGIN_NAME"]
        #     feature = match_obj["FEATURE"]
        #     meta_key = match_obj["META_KEY"]
        #     if feature == "connector":
        #         plugin_connector_dict = self.__connectors.setdefault(plugin_name, {})
        #         plugin_connector_dict[meta_key] = value


