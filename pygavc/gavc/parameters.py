import os

class Param:
    __ENV     = 'env'
    __VALUE   = 'value'
    __REQUIRED= 'required'

    def __validate(self):
        if not self.__required:
            return

        if self.__env and self.__value is None:
            raise Exception("Required enviroment variable '%s' is not set!" % self.__env)

    def __init__(self, **kwargs):
        self.__required = kwargs[self.__REQUIRED] if self.__REQUIRED in kwargs else False
        self.__env      = kwargs[self.__ENV] if self.__ENV in kwargs else None
        self.__value    = kwargs[self.__VALUE] if self.__VALUE in kwargs else None
        self.__value    = os.environ.get(self.__env, self.__value) if self.__env else self.__value
        self.__validate()

    def env(self):
        return self.__env

    def set(self, value):
        self.__value = value

    def get(self, default_value):
        return self.__value if self.__value else default_value


class BaseParamsHandler:
    TOKEN_PARAM         = 'token'
    SERVER_PARAM        = 'server'
    REPOSITORY_PARAM    = 'repository'

    class NotSupportedParamSet(Exception):
        def __init__(self, name):
            Exception.__init__("Attempt to set value for not supported parameter: '%s'!" % name)

    class NotSupportedParamGet(Exception):
        def __init__(self, name):
            Exception.__init__("Attempt to get value of not supported parameter: '%s'!" % name)

    def __init__(self):
        self._params = {
            BaseParamsHandler.TOKEN_PARAM         : Param(env="GAVC_SERVER_API_ACCESS_TOKEN", required=True),
            BaseParamsHandler.SERVER_PARAM        : Param(env="GAVC_SERVER_URL", required=True),
            BaseParamsHandler.REPOSITORY_PARAM    : Param(env="GAVC_SERVER_REPOSITORY", required=True),
        }

    def set_param(self, name, value):
        if not name in self._params:
            raise BaseParamsHandler.NotSupportedParamSet(name)
        self._params[name].set(value)

    def get_param(self, name, default_value = None):
        if not name in self._params:
            raise NotSupportedParamGet(name)
        return self._params[name].get(default_value)


class GavcClientParamsHandler(BaseParamsHandler):
    CACHE_PATH_PARAM                    = 'cache-path'
    CACHE_MAX_NO_ACCESS_ASSET_AGE       = 'cache-max-no-access-asset-age'
    FORCE_OFFLINE_PARAM                 = 'force-offline'

    def __init__(self):
        BaseParamsHandler.__init__(self)
        default_cache_path = os.path.join(os.path.expanduser("~"), ".gavc")
        self._params.update({
            GavcClientParamsHandler.CACHE_PATH_PARAM                : Param(env="GAVC_CACHE", value=default_cache_path),
            GavcClientParamsHandler.CACHE_MAX_NO_ACCESS_ASSET_AGE   : Param(env="GAVC_CACHE_MAX_NO_ACCESS_ASSET_AGE", value="2678400"),
            GavcClientParamsHandler.FORCE_OFFLINE_PARAM             : Param(env="GAVC_FORCE_OFFLINE")
        })


def main():
    ph = GavcClientParamsHandler()

    print(ph.get_param(BaseParamsHandler.TOKEN_PARAM))
    ph.set_param(BaseParamsHandler.TOKEN_PARAM, "12234")
    print(ph.get_param(BaseParamsHandler.TOKEN_PARAM))
    print(ph.get_param(BaseParamsHandler.TOKEN_PARAM, "11111"))

if __name__ == "__main__":
    main()
