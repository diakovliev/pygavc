import os
import sqlite3

class BaseDatabase:

    # CREATE_TABLES

    MEMORY_FILENAME = ":memory:"

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
        new_database = not os.path.isfile(self.__filename)
        self.__conn = sqlite3.connect(self.__filename)
        if new_database:
            self.__create_tables()

        return self.__conn
