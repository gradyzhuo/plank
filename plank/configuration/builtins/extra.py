from ..info import ConfigInfo

class ExtraConfigInfo(ConfigInfo):

    def __configure__(self):
        collections = {}
        prefix = f"{self.namespace}."
        for keyspace, value in self.config_dict.items():
            clearified_keyspace = keyspace.replace(prefix, "")
            keys = clearified_keyspace.split(".")

            extra_key = keys[0]

            sub_keys = keys[2:-1]
            if len(sub_keys) > 0:
                config_dict = collections.setdefault(extra_key, {})
                for sub_key in sub_keys:
                    config_dict = config_dict.setdefault(sub_key, {})
                config_dict[keys[-1]] = value

            else:
                if isinstance(value, list):
                    config_array = collections.setdefault(extra_key, [])
                    config_array.extend(value)
                else:
                    collections.setdefault(extra_key, value)
        self._collections = collections


    def keys(self):
        return self._collections.keys()

    def __getitem__(self, item):
        return self._collections[item]