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

        # print(" - Load user config '%s'" % UserConfig.path())
        with open(UserConfig.path(), 'r') as f:
            values = yaml.safe_load(f)

        if values is None:
            values = {}

        return UserConfig(values)

    def store(self):
        # print(" - Store user config '%s'" % UserConfig.path())
        with open(UserConfig.path(), 'w') as f:
            yaml.dump(self.__values, f)

    def read_value(self, key):
        return self.get_value(key)

    def set_value(self, key, value):
        self.__values[key] = value

    def del_value(self, key):
        del self.__values[key]

    def get_value(self, key, default_value = None):
        return self.__values.get(key, default_value)
