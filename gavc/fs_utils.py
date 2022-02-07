import os
import filelock


class DirectoryLock:
    __LOCK_SFX = ".dirlock"

    def __init__(self, dirpath):
        self.__dirpath          = dirpath
        self.__lock_filename    = os.path.join(self.__dirpath, os.path.basename(self.__dirpath) + self.__LOCK_SFX)

    def __enter__(self):
        self.__lock = filelock.FileLock(self.__lock_filename)
        self.__lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release(force=True)
        self.__lock = None
        FsUtils.remove(self.__lock_filename)



class FsUtils:
    @staticmethod
    def ensure_dir(dirpath):
        if not os.path.isdir(dirpath): os.makedirs(dirpath, exist_ok = True)
        return dirpath

    @staticmethod
    def ensure_parent_dir(filepath):
        return FsUtils.ensure_dir(os.path.abspath(os.path.join(filepath, os.pardir)))

    @staticmethod
    def directory_lock(dirpath):
        return DirectoryLock(dirpath)

    @staticmethod
    def remove(path, ignore_errors = True):
        try:
            os.remove(path)
        except FileNotFoundError as error:
            if not ignore_errors:
                raise error
        except OSError as error:
            if not ignore_errors:
                raise error
        return os.path.exists(path)

    @staticmethod
    def remove_collection(files, ignore_errors = True):
        for fp in files:
            FsUtils.remove(fp, ignore_errors)
