import os
import sqlite3
import filelock

from .fs_utils import FsUtils

class BaseDatabase:

    # CREATE_TABLES

    MEMORY_FILENAME = ":memory:"
    __LOCK_SFX      = ".lock"

    def __init__(self, filename = MEMORY_FILENAME):
        self.__filename = filename
        self.__conn     = None

        self.open()


    def _cursor(self):
        assert not self.__conn is None

        return self.__conn.cursor()


    def _commit(self):
        assert not self.__conn is None

        self.__conn.commit()


    def __create_tables(self):
        cursor = self._cursor()

        cursor.executescript(self.CREATE_TABLES)

        self._commit()


    def open(self):
        if self.__filename != self.MEMORY_FILENAME:
            FsUtils.ensure_parent_dir(self.__filename)

            with filelock.FileLock(self.__filename + self.__LOCK_SFX):
                new_database = not os.path.isfile(self.__filename)
                self.__conn = sqlite3.connect(self.__filename)
                if new_database:
                    self.__create_tables()

        else:
            self.__conn = sqlite3.connect(self.__filename)
            self.__create_tables()

        return self.__conn
