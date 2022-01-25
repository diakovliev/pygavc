import os
import filecmp
import shutil

from parameters import GavcClientParamsHandler

class ArtifactoryObjectsCache:
    SUBROOT_DIR = "pygavc"
    OBJECTS_DIR = "objects"

    def __init__(self, client):
        self.__client       = client
        self.__storage_root = os.path.join(client.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM), self.SUBROOT_DIR, self.OBJECTS_DIR)
        # TODO: Move to cache initializer
        if not os.path.isdir(self.__storage_root): os.makedirs(self.__storage_root)

    def enabled(self):
        return True

    def storage_root(self):
        return self.__storage_root

    def asset_path(self, asset):
        checksum = asset.sha1()
        p0 = checksum[:2]
        p1 = checksum[2:4]
        p2 = checksum[4:]
        return os.path.join(self.storage_root(), p0, p1, p2)

    def contains(self, asset):
        return os.path.isfile(self.asset_path(asset))

    def validate_destination(self, asset, destination_path):
        if not os.path.isfile(destination_path):
            return False
        return filecmp.cpm(self.asset_path(asset), destination_path, False)

    def move_file(self, source_path, destination_path):
        shutil.move(source_path, destination_path)

    def copy_asset(self, asset, destination_path):
        shutil.copy(self.asset_path(asset), destination_path)
