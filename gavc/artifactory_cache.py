import os

from .parameters import GavcClientParamsHandler
from .artifactory_requests_cache import ArtifactoryRequestsCache
from .artifactory_objects_cache import ArtifactoryObjectsCache
from .fs_utils import FsUtils

class ArtifactoryCache:
    SUBROOT_DIR     = 'pygavc'
    OBJECTS_DIR     = "objects"
    DOWNLOADS_DIR   = "dowloads"
    DATABASE_FILE   = 'requests.db'

    def __subelement_path(self, element_name = ""):
        return os.path.join(self.__client.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM), self.SUBROOT_DIR, element_name)

    def __init__(self, client):
        self.__enabled  = True
        self.__client   = client
        self.__root     = FsUtils.ensure_dir(self.__subelement_path())

        self.__objects  = ArtifactoryObjectsCache(
            os.path.join(self.__root, self.OBJECTS_DIR),
            os.path.join(self.__root, self.DOWNLOADS_DIR),
            int(client.get_param(GavcClientParamsHandler.CACHE_MAX_NO_ACCESS_ASSET_AGE))
        ).initialize()

        self.__requests = ArtifactoryRequestsCache(
            os.path.join(self.__root, self.DATABASE_FILE)
        ).initialize()

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
