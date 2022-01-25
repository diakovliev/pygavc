import os
import hashlib

from parameters import GavcClientParamsHandler

class ArtifactoryRequestsCache:
    ENCODING = 'utf-8'

    SUBROOT_DIR = 'pygavc'
    DATABASE_FILE = 'requests.db'

    def __init__(self, client):
        self.__client   = client
        self.__storage  = os.path.join(client.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM), self.SUBROOT_DIR, self.DATABASE_FILE)
        self.__cache    = {}

    def enabled(self):
        return True

    def __cache_key(self, selector0, selector1 = None):
        data = selector0.encode(self.ENCODING)
        if selector1:
            data += selector1.encode(self.ENCODING)
        return hashlib.sha256(data).hexdigest()

    def contains_post(self, query, data):
        cache_key = self.__cache_key(query, data)
        return cache_key in self.__cache

    def post(self, query, data):
        cache_key = self.__cache_key(query, data)
        return self.__cache[cache_key]

    def contains_get(self, query):
        return self.contains_post(query, None)

    def get(self, query):
        return self.post(query, None)

    def update_get(self, query, query_result):
        return self.update_post(query, None, query_result)

    def update_post(self, query, data, query_result):
        cache_key = self.__cache_key(query, data)
        self.__cache[cache_key] = query_result
        return query_result
