from polymath.config.info import ConfigInfo
import re
from typing import Dict, Any

class PluginConfig(ConfigInfo):

    @property
    def prefix(self)->str:
        return self.get("prefix")

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


    def connector_dict(self, plugin_name: str)->Dict[str, Any]:
        if plugin_name in self.__connectors.keys():
            return self.__connectors[plugin_name]
        else:
            return self.__connectors["__all__"]

    def connector_base_url(self, plugin_name: str)->str:
        connector_dict=  self.connector_dict(plugin_name=plugin_name)
        scheme = connector_dict['scheme']
        host = connector_dict['host']
        port = connector_dict.get("port")
        url = f"{scheme}://{host}"
        if port is not None:
            return f"{url}:port"
        else:
            return url
