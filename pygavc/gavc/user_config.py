import os
import yaml

class UserConfig:
    _CONFIG_FILENAME = ".pygavc_config.yaml"

    def __init__(self, values):
        self.__values = values

    @staticmethod
    def path():
        return os.path.join(os.path.expanduser("~"), UserConfig._CONFIG_FILENAME)

    @staticmethod
    def load():
        if not os.path.isfile(UserConfig.path()):
            return UserConfig({})

        print(" - Load user config '%s'" % UserConfig.path())
        with open(UserConfig.path(), 'rb') as f:
            values = yaml.safe_load(f)

        return UserConfig(values)

    def read_value(self, key):
        return self.__values.get(key, None)
