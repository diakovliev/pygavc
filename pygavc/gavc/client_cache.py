import os

from .gavc_parameters import GavcClientParamsHandler
from .requests_cache import RequestsCache
from .objects_cache import ObjectsCache
from .fs_utils import FsUtils

class ClientCache(object):
    SUBROOT_DIR     = 'pygavc'
    OBJECTS_DIR     = "objects"
    DOWNLOADS_DIR   = "dowloads"
    DATABASE_FILE   = 'requests.db'

    def __subelement_path(self, element_name = ""):
        return os.path.join(self.__cache_path, self.SUBROOT_DIR, element_name)

    def __init__(self, cache_path, max_no_access_asset_time):
        self.__enabled                  = True
        self.__cache_path               = cache_path
        self.__max_no_access_asset_time = max_no_access_asset_time
        self.__root                     = FsUtils.ensure_dir(self.__subelement_path())

        self.__objects  = ObjectsCache(
            os.path.join(self.__root, self.OBJECTS_DIR),
            os.path.join(self.__root, self.DOWNLOADS_DIR),
            max_no_access_asset_time,
        ).initialize()

        self.__requests = RequestsCache(
            os.path.join(self.__root, self.DATABASE_FILE)
        ).initialize()

    @staticmethod
    def from_params_handler(params_handler = GavcClientParamsHandler()):
        cache_path                  = params_handler.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM)
        max_no_access_asset_time    = int(params_handler.get_param(GavcClientParamsHandler.CACHE_MAX_NO_ACCESS_ASSET_AGE))
        return ClientCache(cache_path, max_no_access_asset_time)

    def enabled(self):
        return self.__enabled

    def set_enabled(self, enabled):
        self.__enabled = enabled

    def disable(self):
        self.set_enabled(False)

    def enable(self):
        self.set_enabled(True)

    def objects(self):
        return self.__objects

    def requests(self):
        return self.__requests
