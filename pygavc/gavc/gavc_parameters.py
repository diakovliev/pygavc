import os
from .parameters import BaseParamsHandler

class GavcClientBaseParamsHandler(BaseParamsHandler):
    TOKEN_PARAM         = 'token'
    SERVER_PARAM        = 'server'
    REPOSITORY_PARAM    = 'repository'

    DEFAULT_GAVC_SERVER_URL                 = "https://artifactory.developonbox.ru/artifactory"
    DEFAULT_GAVC_SERVER_REPOSITORY          = "bin-release-local"
    DEFAULT_GAVC_SERVER_API_ACCESS_TOKEN    = "<invalid token>"

    def __init__(self):
        BaseParamsHandler.__init__(self)
        self._add_parameter(GavcClientBaseParamsHandler.TOKEN_PARAM, [
            self._ValueSourceEnv("GAVC_SERVER_API_ACCESS_TOKEN"),
            self._ValueSourceUserConfig(GavcClientBaseParamsHandler.TOKEN_PARAM),
            self._ValueSourceConst(self.DEFAULT_GAVC_SERVER_API_ACCESS_TOKEN),
        ], required=True, hidden=True)
        self._add_parameter(GavcClientBaseParamsHandler.SERVER_PARAM, [
            self._ValueSourceEnv("GAVC_SERVER_URL"),
            self._ValueSourceUserConfig(GavcClientBaseParamsHandler.SERVER_PARAM),
            self._ValueSourceConst(self.DEFAULT_GAVC_SERVER_URL),
        ], required=True)
        self._add_parameter(GavcClientBaseParamsHandler.REPOSITORY_PARAM, [
            self._ValueSourceEnv("GAVC_SERVER_REPOSITORY"),
            self._ValueSourceUserConfig(GavcClientBaseParamsHandler.REPOSITORY_PARAM),
            self._ValueSourceConst(self.DEFAULT_GAVC_SERVER_REPOSITORY),
        ], required=True)


class GavcClientParamsHandler(GavcClientBaseParamsHandler):
    CACHE_PATH_PARAM                    = 'cache-path'
    CACHE_MAX_NO_ACCESS_ASSET_AGE       = 'cache-max-no-access-asset-age'
    FORCE_OFFLINE_PARAM                 = 'force-offline'

    def __init__(self):
        GavcClientBaseParamsHandler.__init__(self)
        self._add_parameter(GavcClientParamsHandler.CACHE_PATH_PARAM, [
            self._ValueSourceEnv("GAVC_CACHE"),
            self._ValueSourceUserConfig(GavcClientParamsHandler.CACHE_PATH_PARAM),
            self._ValueSourceConst(os.path.join(os.path.expanduser("~"), ".gavc"))
        ])
        self._add_parameter(GavcClientParamsHandler.CACHE_MAX_NO_ACCESS_ASSET_AGE, [
            self._ValueSourceEnv("GAVC_CACHE_MAX_NO_ACCESS_ASSET_AGE"),
            self._ValueSourceUserConfig(GavcClientParamsHandler.CACHE_MAX_NO_ACCESS_ASSET_AGE),
            self._ValueSourceConst("2678400")
        ])
        self._add_parameter(GavcClientParamsHandler.FORCE_OFFLINE_PARAM, [
            self._ValueSourceEnv("GAVC_FORCE_OFFLINE"),
            self._ValueSourceConst("0")
        ])


def main():
    ph = GavcClientParamsHandler()

    print(ph.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM))
    ph.set_param(GavcClientBaseParamsHandler.TOKEN_PARAM, "12234")
    print(ph.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM))
    print(ph.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM, "11111"))

if __name__ == "__main__":
    main()
