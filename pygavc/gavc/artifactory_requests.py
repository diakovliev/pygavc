import os
import sys
import requests
import time
import filelock

from .metadata import Metadata
from .aql import AqlResults
from .file_downloader import FileDownloader

from ..functional.bind import Bind

class ArtifactoryRequests:
    HTTP_OK         = 200
    HTTP_CREATED    = 201
    HTTP_ACEPTED    = 202

    SOURCE_ORIGIN   = 'origin'
    SOURCE_CACHE    = 'cache'

    HTTP_METHOD_GET = 'GET'
    HTTP_METHOD_POST= 'POST'

    class Error(Exception):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    class HttpError(Error):
        def __init__(self, status_code):
            ArtifactoryRequests.Error.__init__(self)
            self.__status_code = status_code

        def __str__(self):
            return "Http error. Code '%d'." % self.__status_code


    def make_http_error(self, status_code):
        return self.HttpError(status_code)


    def __init__(self, client):
        self.__client                   = client
        self.__session                  = None
        self.__max_download_attempts    = 5


    def session(self):
        if not self.__session:
            self.__session = requests.Session()
        return self.__session


    def get2(self, query, **kwargs):
        """
            HTTP get. Uncached version.
        """
        kwargs['headers'] = self.__client.headers()
        return self.session().get(query, **kwargs)


    def put2(self, query, **kwargs):
        """
            HTTP put. Uncached version.
        """
        kwargs['headers'] = self.__client.headers()
        r = self.session().put(query, **kwargs)
        if r.status_code not in [ self.HTTP_OK, self.HTTP_CREATED, self.HTTP_ACEPTED ]:
            raise self.make_http_error(r.status_code)
        return r


    def post2(self, query, data, **kwargs):
        """
            HTTP post. Uncached version.
        """
        kwargs['headers'] = self.__client.headers()
        kwargs['data'] = data
        return self.session().post(query, **kwargs)


    def __cached_request(self, cache_contains, cache_get, cache_update, request_get, primary_source = SOURCE_CACHE, method = HTTP_METHOD_GET):
        """
            HTTP get. Cached version.
        """
        if not self.__client.cache().enabled():
            return request_get()

        cache = self.__client.cache().requests()
        if primary_source == self.SOURCE_ORIGIN:
            print(" - %s '%s' update cache" % (method, request_get))
            r = request_get()
            if r.status_code != self.HTTP_OK:
                if not cache_contains():
                    return r
                print(" - %s(cached) '%s' use cached result" % (method, cache_get))
                return cache_get()
        elif primary_source == self.SOURCE_CACHE:
            if cache_contains():
                print(" - %s(cached) '%s' use cached result" % (method, cache_get))
                return cache_get()
            print(" - %s '%s' update cache" % (method, request_get))
            r = request_get()
            if r.status_code != self.HTTP_OK:
                return r

        return cache_update(r)


    def get(self, query, primary_source = SOURCE_CACHE):
        cache = self.__client.cache().requests()
        return self.__cached_request(
            Bind(cache.contains_get, query),
            Bind(cache.get, query),
            Bind(cache.update_get, query),
            Bind(self.get2, query),
            primary_source,
            self.HTTP_METHOD_GET
        )


    def post(self, query, data, primary_source = SOURCE_CACHE):
        cache = self.__client.cache().requests()
        return self.__cached_request(
            Bind(cache.contains_post, query, data),
            Bind(cache.post, query, data),
            Bind(cache.update_post, query, data),
            Bind(self.post2, query, data),
            primary_source,
            self.HTTP_METHOD_POST
        )


    def metadata_for(self, query):
        metadata_url = self.__client.repository_url(query.metadata_path())
        r = self.get(metadata_url, self.SOURCE_ORIGIN)
        if r.status_code != self.HTTP_OK:
            raise self.make_http_error(r.status_code)
        return Metadata.parse(r.text)


    def perform_aql(self, aql):
        r = self.post(self.__client.aql_url(), aql, self.SOURCE_ORIGIN)
        if r.status_code != self.HTTP_OK:
            raise self.make_http_error(r.status_code)
        return AqlResults.parse(r.text, self.__client.url())


    def versions_for(self, query):
        return self.metadata_for(query).versions_for(query)


    def assets_for(self, query):
        for version in self.versions_for(query):
            for sq in self.__client.resolved_queries_for(query, version):
                assets = self.perform_aql(sq.to_aql_query())
                if not assets:
                    return
                for asset in assets:
                    yield asset


    def __download_file(self, destination_file, url, enable_progress_bar=True):
        return FileDownloader(self, destination_file, url, enable_progress_bar)()


    def __download_asset(self, cache, asset, enable_progress_bar=True):
        dwn_lock = cache.dwn_lock(asset)

        try:
            with dwn_lock.acquire(timeout=1):
                self.__download_file(cache.dwn_path(asset), asset.url(), enable_progress_bar)
                cache.commit_asset(asset)

        except KeyboardInterrupt as ki:
            raise ki

        except filelock.Timeout as timeout:
            while True:
                try:
                    dwn_lock.acquire(timeout=1)
                    break

                except KeyboardInterrupt as ki:
                    raise ki

                except filelock.Timeout as timeout:
                    # print("Wait while another client will download needed object...")
                    pass


    class DestinationFileAccessWrapper:
        def __init__(self, destination_file):
            self__destination_file = destination_file

        def path(self):
            return self.__destination_file

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass


    class CacheAssetAccessWrapper:
        def __init__(self, asset_path, asset_locked_lock):
            self.__asset_path   = asset_path
            self.__asset_lock   = asset_locked_lock

        def path(self):
            return self.__asset_path

        def __enter__(self):
            assert self.__asset_lock.is_locked
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            assert self.__asset_lock.is_locked
            self.__asset_lock.release(force=True)
            self.__asset_lock = None


    def __handle_cache(self, cache, asset, destination_file):
        if not cache.contains(asset):
            return None

        asset_lock = cache.asset_lock(asset)
        asset_lock.acquire()

        cache.update_access(asset)
        if destination_file is None:
            print(" - Return cache object: '%s'" % asset.url())
            return self.CacheAssetAccessWrapper(cache.asset_path(asset), asset_lock)

        asset_lock.release()

        if cache.validate_destination(asset, destination_file):
            print(" - Destination '%s' is actual" % destination_file)
            return self.DestinationFileAccessWrapper(destination_file)

        print("Extract cache object '%s' -> '%s'" % (asset.url(), destination_file))
        cache.copy_asset(asset, destination_file)
        return self.DestinationFileAccessWrapper(destination_file)


    def retrieve_asset(self, asset, destination_file = None, enable_progress_bar=True, attempt=0):
        if not self.__client.cache().enabled():
            assert destination_file is not None, "Requested direct download without destination_file!"
            print(" - Direct download file '%s' -> '%s'" % (asset.url(), destination_file))
            self.__download_file(destination_file, asset.url(), enable_progress_bar)
            return destination_file

        cache = self.__client.cache().objects()

        result_path = self.__handle_cache(cache, asset, destination_file)
        if result_path is not None:
            return result_path

        print(" - Download asset '%s' into cache. Attempt %d" % (asset.url(), attempt))
        self.__download_asset(cache, asset, enable_progress_bar)

        result_path = self.__handle_cache(cache, asset, destination_file)
        if result_path is not None:
            return result_path

        if attempt < self.__max_download_attempts:
            print(" - No asset in cache, try to download it agait...")
            return self.retrieve_asset(asset, destination_file, enable_progress_bar, attempt+1)

        raise self.Error("Asset '%s' download error!" % asset.url())
        return None
