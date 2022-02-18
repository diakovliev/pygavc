import os
import filecmp
import shutil
import filelock
import datetime
import glob
import yaml
import hashlib

from .fs_utils import FsUtils

class ObjectsCache:

    LOCK_SFX = ".lock"
    PROPS_SFX = ".yaml"
    TEMP_SFX = ".temp"

    ACCESS_TIME = "access_time"
    DATETIME_FMT = "%m-%d-%Y %H:%M:%S UTC"

    def __init__(self, storage_root, downloads_root, max_no_access_asset_age):
        self.__storage_root             = storage_root
        self.__downloads_root           = downloads_root
        self.__max_no_access_asset_age  = max_no_access_asset_age

    def initialize(self):
        return self

    def storage_root(self):
        return self.__storage_root

    def downloads_root(self):
        return self.__downloads_root

    def __asset_checksum(self, asset):
        checksum = asset.sha1()
        assert checksum
        assert len(checksum) > 4
        return checksum

    def __asset_subpath(self, asset):
        checksum = self.__asset_checksum(asset)
        p0 = checksum[:2]
        p1 = checksum[2:4]
        p2 = checksum[4:]
        return os.path.join(p0, p1, p2)

    def asset_path(self, asset):
        return os.path.join(self.storage_root(), self.__asset_subpath(asset))

    def dwn_path(self, asset):
        checksum = self.__asset_checksum(asset)
        return os.path.join(self.downloads_root(), checksum)

    def props_path(self, asset):
        return self.asset_path(asset) + self.PROPS_SFX

    def __dwn_lock_path(self, asset):
        return self.dwn_path(asset) + self.LOCK_SFX

    def __asset_lock_path(self, asset):
        return self.asset_path(asset) + self.LOCK_SFX

    def dwn_lock(self, asset):
        dwn_file_lock = self.__dwn_lock_path(asset)
        FsUtils.ensure_parent_dir(dwn_file_lock)
        return filelock.FileLock(dwn_file_lock)

    def asset_lock(self, asset):
        asset_file_lock = self.__asset_lock_path(asset)
        FsUtils.ensure_parent_dir(asset_file_lock)
        return filelock.FileLock(asset_file_lock)

    def contains(self, asset):
        return os.path.isfile(self.asset_path(asset))

    def validate_asset(self, asset, buf_size = 1024 * 1024):
        asset_checksum      = asset.sha1()
        object_path         = self.asset_path(asset)

        sha1 = hashlib.sha1()

        with open(object_path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                sha1.update(data)

        object_checksumm = sha1.hexdigest()

        return asset_checksum == object_checksumm

    def remove_asset(self, asset):
        FsUtils.remove(self.props_path(asset))
        FsUtils.remove(self.asset_path(asset))

    def validate_destination(self, asset, destination_path):
        with self.asset_lock(asset):
            if not os.path.isfile(destination_path):
                return False
            return filecmp.cmp(self.asset_path(asset), destination_path, False)

    def commit_asset(self, asset):
        destination_path    = self.asset_path(asset)
        FsUtils.ensure_parent_dir(destination_path)
        with self.asset_lock(asset):
            source_path     = self.dwn_path(asset)
            self.update_access(asset)
            shutil.move(source_path, destination_path)
            FsUtils.remove(self.__dwn_lock_path(asset))

    def copy_asset(self, asset, destination_path):
        with self.asset_lock(asset):
            shutil.copy(self.asset_path(asset), destination_path)


    def __read_last_access(self, props_file):
        assert os.path.isfile(props_file)
        with open(props_file, 'r') as f:
            props = yaml.safe_load(f)
        assert self.ACCESS_TIME in props
        return datetime.datetime.strptime(props[self.ACCESS_TIME], self.DATETIME_FMT)


    def update_access(self, asset):
        now     = datetime.datetime.utcnow()
        strtime = datetime.datetime.strftime(now, self.DATETIME_FMT)
        props = { self.ACCESS_TIME: strtime }
        with open(self.props_path(asset) + self.TEMP_SFX, 'w') as f:
            yaml.dump(props, f)
        shutil.move(self.props_path(asset) + self.TEMP_SFX, self.props_path(asset))


    def clean(self):
        clean_table = {}

        for filename in glob.iglob("%s/**/**" % self.__storage_root, recursive=True):
            if os.path.isdir(filename):
                continue
            if os.path.abspath(filename) == os.path.abspath(self.__storage_root):
                continue
            if filename.endswith(self.LOCK_SFX):
                continue
            if filename.endswith(self.PROPS_SFX):
                continue
            if filename.endswith(self.TEMP_SFX):
                continue

            asset_path  = filename
            props_path  = asset_path + self.PROPS_SFX
            last_access = self.__read_last_access(props_path)
            timedelta   = datetime.datetime.utcnow() - last_access

            clean_table[asset_path] = timedelta.total_seconds()

        for key, value in clean_table.items():
            if value > self.__max_no_access_asset_age:
                asset_lock_path = key + self.LOCK_SFX
                asset_lock      = filelock.FileLock(asset_lock_path)
                try:
                    asset_lock.acquire(timeout=0)
                    FsUtils.remove_collection([
                        key,
                        key + self.PROPS_SFX,
                        key + self.PROPS_SFX + self.TEMP_SFX,
                    ])
                    asset_lock.release(force=True)
                    FsUtils.remove(asset_lock_path)
                except filelock.Timeout as tm:
                    # Can't lock asset. Skip..
                    pass
