import os
import sys
import requests
import time
import filelock

from .metadata import Metadata
from .aql import AqlResults
from .file_downloader import FileDownloader
from .cached_requests import CachedRequests

from ..functional.bind import Bind

################################################################################
class ArtifactoryRequests(CachedRequests):

    DEF_MAX_DOWNLOAD_ATTEMPTS = 5

    def __init__(self, client):
        CachedRequests.__init__(self, client)
        self.__max_download_attempts = self.DEF_MAX_DOWNLOAD_ATTEMPTS


    def get_local_repos(self):
        r = self.get2(self.client().get_local_repos_request())
        if r.status_code != self.HTTP_OK:
            raise self.make_http_error(r.status_code)
        return r


    def metadata_for(self, query):
        metadata_url = self.client().repository_url(query.metadata_path())
        r = self.get(metadata_url, self.SOURCE_ORIGIN)
        if r.status_code != self.HTTP_OK:
            raise self.make_http_error(r.status_code)
        return Metadata.parse(r.text)


    def perform_aql(self, aql):
        r = self.post(self.client().aql_url(), aql, self.SOURCE_ORIGIN)
        if r.status_code != self.HTTP_OK:
            raise self.make_http_error(r.status_code)
        return AqlResults.parse(r.text, self.client().url())


    def versions_for(self, query):
        return self.metadata_for(query).versions_for(query)


    def assets_for(self, query):
        for version in self.versions_for(query):
            for sq in self.client().resolved_queries_for(query, version):
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

        if not cache.validate_asset(asset):
            cache.remove_asset(asset)
            asset_lock.release()
            return None

        cache.update_access(asset)
        if destination_file is None:
            # print(" - Return cache object: '%s'" % asset.url())
            return self.CacheAssetAccessWrapper(cache.asset_path(asset), asset_lock)

        if cache.validate_destination(asset, destination_file):
            # print(" - Destination '%s' is actual" % destination_file)
            asset_lock.release()
            return self.DestinationFileAccessWrapper(destination_file)

        # print("Extract cache object '%s' -> '%s'" % (asset.url(), destination_file))
        cache.copy_asset(asset, destination_file)
        asset_lock.release()

        return self.DestinationFileAccessWrapper(destination_file)


    def retrieve_asset(self, asset, destination_file = None, enable_progress_bar=True, attempt=0):
        if not self.client().cache().enabled():
            assert destination_file is not None, "Requested direct download without destination_file!"
            # print(" - Direct download file '%s' -> '%s'" % (asset.url(), destination_file))
            self.__download_file(destination_file, asset.url(), enable_progress_bar)
            return destination_file

        cache = self.client().cache().objects()

        result_path = self.__handle_cache(cache, asset, destination_file)
        if result_path is not None:
            return result_path

        # print(" - Download asset '%s' into cache. Attempt %d" % (asset.url(), attempt))
        self.__download_asset(cache, asset, enable_progress_bar)

        result_path = self.__handle_cache(cache, asset, destination_file)
        if result_path is not None:
            return result_path

        if attempt < self.__max_download_attempts:
            # print(" - No asset in cache, try to download it agait...")
            return self.retrieve_asset(asset, destination_file, enable_progress_bar, attempt+1)

        raise self.Error("Asset '%s' download error!" % asset.url())
        return None
