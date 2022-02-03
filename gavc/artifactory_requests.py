import os
import sys
import requests
import tqdm

from .metadata import Metadata
from .simple_query import AqlResults
from functions.bind import Bind


class ArtifactoryRequests:
    HTTP_OK = 200

    SOURCE_CACHE    = 'cache'
    SOURCE_ORIGIN   = 'origin'

    class HttpError:
        def __init__(self, status_code):
            self.__status_code = status_code


    def __init__(self, client):
        self.__client   = client
        self.__session  = None

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

    def post2(self, query, data, **kwargs):
        """
            HTTP post. Uncached version.
        """
        kwargs['headers'] = self.__client.headers()
        kwargs['data'] = data
        return self.session().post(query, **kwargs)

    def __cached_request(self, cache_contains, cache_get, cache_update, request_get, primary_source = SOURCE_CACHE):
        """
            HTTP get. Cached version.
        """
        if not self.__client.cache().enabled():
            return request_get()

        # TODO: Lock requests cache
        cache = self.__client.cache().requests()
        if primary_source == self.SOURCE_CACHE:
            if cache_contains():
                print("GET(cached) '%s' use cached result" % cache_get)
                return cache_get()
            print("GET '%s' update cache" % request_get)
            r = request_get()
            if r.status_code != self.HTTP_OK:
                return r
        elif primary_source == self.SOURCE_ORIGIN:
            print("GET '%s' update cache" % request_get)
            r = request_get()
            if r.status_code != self.HTTP_OK:
                if not cache_contains():
                    return r
                print("GET(cached) '%s' use cached result" % cache_get)
                return cache_get()

        return cache_update(r)

    def get(self, query, primary_source = SOURCE_CACHE):
        cache = self.__client.cache().requests()
        return self.__cached_request(
            Bind(cache.contains_get, query),
            Bind(cache.get, query),
            Bind(cache.update_get, query),
            Bind(self.get2, query),
            primary_source
        )

    def post(self, query, data, primary_source = SOURCE_CACHE):
        cache = self.__client.cache().requests()
        return self.__cached_request(
            Bind(cache.contains_post, query, data),
            Bind(cache.post, query, data),
            Bind(cache.update_post, query, data),
            Bind(self.post2, query, data),
            primary_source
        )


    def metadata_for(self, query):
        metadata_url = self.__client.repository_metadata_url(query.metadata_path())
        r = self.get(metadata_url, self.SOURCE_ORIGIN)
        if r.status_code != self.HTTP_OK:
            raise self.HttpError(r.status_code)
        return Metadata.parse(r.text)

    def perform_aql(self, aql):
        r = self.post(self.__client.aql_url(), aql, self.SOURCE_ORIGIN)
        if r.status_code != self.HTTP_OK:
            raise self.HttpError(r.status_code)
        return AqlResults.parse(r.text, self.__client.url())

    def assets_for(self, query):
        for version in self.metadata_for(query).versions_for(query):
            for sq in self.__client.simple_queries_for(query, version):
                for asset in self.perform_aql(sq.to_aql_query()):
                    yield asset

    def __download_file(self, destination_file, url, enable_progress_bar=True):
        # TODO: Lock destination

        destination_parent_path = os.path.abspath(os.path.join(destination_file, os.pardir))
        if not os.path.isdir(destination_parent_path): os.makedirs(destination_parent_path)

        r = self.get2(url, stream=True)
        if r.status_code != self.HTTP_OK:
            raise self.HttpError(r.status_code)

        progress_bar = None
        if enable_progress_bar:
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            block_size          = 1024*1024
            progress_bar        = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with open(destination_file, 'wb') as f:
            for chunk in r.iter_content(block_size):
                if progress_bar: progress_bar.update(len(chunk))
                f.write(chunk)

        if progress_bar: progress_bar.close()

    def retrieve_asset(self, asset, destination_file = None, enable_progress_bar=True):
        if not self.__client.cache().enabled():
            assert destination_file is not None
            print("Download object: '%s'" % asset.url())
            self.__download_file(destination_file, asset.url(), enable_progress_bar)
            return destination_file

        cache = self.__client.cache().objects()
        if cache.contains(asset) and destination_file is None:
            return cache.asset_path(asset)

        if destination_file is not None:
            if cache.contains(asset) and cache.validate_destination(asset, destination_file):
                print("Destination is actual: '%s'" % asset.url())
                return destination_file

            if cache.contains(asset) and not cache.validate_destination(asset, destination_file):
                print("Cached object: '%s'" % asset.url())
                cache.copy_asset(asset, destination_file)
                return destination_file

        # TODO: Lock destination
        print("Download new object: '%s'" % asset.url())
        asset_path          = cache.asset_path(asset)
        temp_file           = asset_path + ".dwn"

        self.__download_file(temp_file, asset.url(), enable_progress_bar)
        cache.move_file(temp_file, asset_path)
        if destination_file is None:
            return asset_path

        cache.copy_asset(asset, destination_file)
        return destination_file
