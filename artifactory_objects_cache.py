import os
import filecmp
import shutil

class ArtifactoryObjectsCache:

    def __init__(self, storage_root):
        self.__storage_root = storage_root

    def initialize(self):
        return self

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
