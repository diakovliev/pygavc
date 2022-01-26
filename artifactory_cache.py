import os

from parameters import GavcClientParamsHandler
from artifactory_requests_cache import ArtifactoryRequestsCache
from artifactory_objects_cache import ArtifactoryObjectsCache


class ArtifactoryCache:
    SUBROOT_DIR     = 'pygavc'
    OBJECTS_DIR     = "objects"
    DATABASE_FILE   = 'requests.db'

    def __subelement_path(self, element_name = ""):
        return os.path.join(self.__client.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM), self.SUBROOT_DIR, element_name)

    def __init__(self, client):
        self.__client   = client
        self.__root     = self.__subelement_path()

        if not os.path.isdir(self.__root): os.makedirs(self.__root)

        self.__objects  = ArtifactoryObjectsCache(os.path.join(self.__root, self.OBJECTS_DIR)).initialize()
        self.__requests = ArtifactoryRequestsCache(os.path.join(self.__root, self.DATABASE_FILE)).initialize()

    def enabled(self):
        return True

    def objects(self):
        return self.__objects

    def requests(self):
        return self.__requests
