import os
import hashlib
import sqlite3

from .base_database import BaseDatabase

class RequestsDatabase(BaseDatabase):
    CREATE_TABLES = """
        CREATE TABLE requests
        (
            key             TEXT NOT NULL,
            query           TEXT,
            data            TEXT,
            text            TEXT NOT NULL,
            CONSTRAINT unique_check UNIQUE(key)
        );
    """

    def insert(self, key, text, query, data):
        cursor = self._cursor()
        cursor.execute("INSERT INTO requests(key, text, query, data) VALUES (?, ?, ?, ?)", (key, text, query, data))
        self._commit()

    def update(self, key, text, query, data):
        cursor = self._cursor()
        cursor.execute("UPDATE requests SET text = ?, query = ?, data = ? WHERE key = ?", (text, query, data, key))
        self._commit()

    def text(self, key):
        cursor = self._cursor()
        result = cursor.execute("SELECT text FROM requests WHERE key = ?", (key,))
        ret = result.fetchall()
        if ret:
            return ret[0][0]
        else:
            return None

    def ensure(self, key, text, query, data):
        try:
            self.insert(key, text, query, data)
        except sqlite3.IntegrityError:
            self.update(key, text, query, data)


class ArtifactoryRequestsCache:
    ENCODING        = 'utf-8'
    SUBROOT_DIR     = 'pygavc'
    HTTP_OK_CODE    = 200

    class Result:
        def __init__(self, status_code, text):
            self.status_code    = status_code
            self.text           = text

    def __init__(self, database):
        self.__db = RequestsDatabase(database)

    def initialize(self):
        return self

    def __db_key(self, selector0, selector1 = None):
        data = selector0.encode(self.ENCODING)
        if selector1:
            data += selector1.encode(self.ENCODING)
        return hashlib.sha256(data).hexdigest()

    def contains_post(self, query, data):
        cache_key = self.__db_key(query, data)
        return self.__db.text(cache_key) is not None

    def post(self, query, data):
        cache_key = self.__db_key(query, data)
        return self.Result(self.HTTP_OK_CODE, self.__db.text(cache_key))

    def contains_get(self, query):
        return self.contains_post(query, None)

    def get(self, query):
        return self.post(query, None)

    def update_get(self, query, query_result):
        return self.update_post(query, None, query_result)

    def update_post(self, query, data, query_result):
        cache_key = self.__db_key(query, data)
        self.__db.ensure(cache_key, query_result.text, query, data)
        return query_result
