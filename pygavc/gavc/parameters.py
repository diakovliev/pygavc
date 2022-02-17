import os

from .user_config import UserConfig

class ValueSource(object):
    pass


class ValueSourceConst(ValueSource):
    _SOURCE_NAME = "default"

    def __init__(self, value):
        ValueSource.__init__(self)
        self.__value = value

    def get(self):
        return self.__value


class ValueSourceEnv(ValueSource):
    _SOURCE_NAME = "env"

    def __init__(self, variable_name):
        ValueSource.__init__(self)
        self.__variable_name = variable_name
        self.__value = None

    def get(self):
        if self.__value is None:
            self.__value = os.environ.get(self.__variable_name)
        return self.__value


class ValueSourceUserConfig(ValueSource):
    __CONFIG = UserConfig.load()
    _SOURCE_NAME = "user config"

    def __init__(self, config_key):
        ValueSource.__init__(self)
        self.__config_key = config_key
        self.__value = None

    def get(self):
        if self.__value is None:
            self.__value = self.__CONFIG.read_value(self.__config_key)
        return self.__value


class Param:
    __REQUIRED  = 'required'
    __HIDDEN    = 'hidden'

    class NotSetParam(Exception):
        def __init__(self, name):
            Exception.__init__(self, "Required parameter '%s' is not set!" % name)

    def __validate(self):
        if not self.__required:
            return

        if self.__value is None:
            raise Param.NotSetParam(self.__name)

    def __init__(self, name, sources, **kwargs):
        self.__name     = name
        self.__required = kwargs[self.__REQUIRED] if self.__REQUIRED in kwargs else False
        self.__hidden   = kwargs[self.__HIDDEN] if self.__HIDDEN in kwargs else False
        self.__sources  = sources
        self.__value    = None
        self.__source   = None

        for value_source in self.__sources:
            self.__value = value_source.get()
            if self.__value is not None:
                self.__source = value_source._SOURCE_NAME
                break

        self.__validate()

    def set(self, value):
        self.__value    = value
        self.__source   = 'set'

    def get(self, default_value):
        return self.__value if self.__value else default_value

    @property
    def source(self):
        return self.__source

    @property
    def hidden(self):
        return self.__hidden

class BaseParamsHandler(object):
    _ValueSourceConst       = ValueSourceConst
    _ValueSourceEnv         = ValueSourceEnv
    _ValueSourceUserConfig  = ValueSourceUserConfig

    class NotSupportedParam(Exception):
        def __init__(self, name):
            Exception.__init__(self, "Not supported parameter: '%s'!" % name)

    def _add_parameter(self, name, sources, **kwargs):
        self._params.update({
            name: Param(
                name,
                sources,
                **kwargs
            )
        })

    def __init__(self):
        self._params = {}

    def set_param(self, name, value):
        if not name in self._params:
            raise BaseParamsHandler.NotSupportedParam(name)
        self._params[name].set(value)

    def get_param(self, name, default_value = None):
        if not name in self._params:
            raise BaseParamsHandler.NotSupportedParam(name)
        return self._params[name].get(default_value)

    def print_all_params(self, header):
        print(header)
        for name, param in self._params.items():
            value = param.get(None)
            if param.hidden and value is not None:
                print("\t'%s' (%s): %s" % (name, param.source, "<hidden>"))
            else:
                print("\t'%s' (%s): '%s'" % (name, param.source, value))
