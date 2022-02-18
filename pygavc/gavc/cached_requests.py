from .requests import Requests
from ..functional.bind import Bind

################################################################################
class CachedRequests(Requests):
    SOURCE_ORIGIN   = 'origin'
    SOURCE_CACHE    = 'cache'

    def __init__(self, client):
        Requests.__init__(self, client)

    def __cached_request(self, cache_contains, cache_get, cache_update, request_get, primary_source = SOURCE_CACHE, method = Requests.HTTP_METHOD_GET):
        """
            HTTP get. Cached version.
        """
        if not self.client().cache().enabled():
            return request_get()

        cache = self.client().cache().requests()
        if primary_source == self.SOURCE_ORIGIN:
            # print(" - %s '%s' update cache" % (method, request_get))
            r = request_get()
            if r.status_code != self.HTTP_OK:
                if not cache_contains():
                    return r
                # print(" - %s(cached) '%s' use cached result" % (method, cache_get))
                return cache_get()
        elif primary_source == self.SOURCE_CACHE:
            if cache_contains():
                # print(" - %s(cached) '%s' use cached result" % (method, cache_get))
                return cache_get()
            # print(" - %s '%s' update cache" % (method, request_get))
            r = request_get()
            if r.status_code != self.HTTP_OK:
                return r

        return cache_update(r)


    def get(self, query, primary_source = SOURCE_CACHE):
        cache = self.client().cache().requests()
        return self.__cached_request(
            Bind(cache.contains_get, query),
            Bind(cache.get, query),
            Bind(cache.update_get, query),
            Bind(self.get2, query),
            primary_source,
            self.HTTP_METHOD_GET
        )


    def post(self, query, data, primary_source = SOURCE_CACHE):
        cache = self.client().cache().requests()
        return self.__cached_request(
            Bind(cache.contains_post, query, data),
            Bind(cache.post, query, data),
            Bind(cache.update_post, query, data),
            Bind(self.post2, query, data),
            primary_source,
            self.HTTP_METHOD_POST
        )
