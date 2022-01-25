import os
import sys
import requests

from metadata import Metadata
from simple_query import AqlResults

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

    def get2(self, query):
        """
            HTTP get. Uncached version.
        """
        return self.session().get(query, headers=self.__client.headers())

    def post2(self, query, data):
        """
            HTTP post. Uncached version.
        """
        return self.session().post(query, headers=self.__client.headers(), data=data)

    def get(self, query, primary_source = SOURCE_CACHE):
        """
            HTTP get. Cached version.
        """
        if not self.__client.requests_cache().enabled():
            return self.get2(query)

        # TODO: Lock requests cache
        cache = self.__client.requests_cache()
        if primary_source == self.SOURCE_CACHE:
            if cache.contains_get(query):
                print("GET(cached) '%s' use cached result" % query)
                return cache.get(query)
            print("GET '%s' update cache" % query)
            r = self.get2(query)
            if r.status_code != self.HTTP_OK:
                return r
        elif primary_source == self.SOURCE_ORIGIN:
            print("GET '%s' update cache" % query)
            r = self.get2(query)
            if r.status_code != self.HTTP_OK:
                if not cache.contains_get(query):
                    return r
                print("GET(cached) '%s' use cached result" % query)
                return cache.get(query)

        return cache.update_get(query, r)

    def post(self, query, data, primary_source = SOURCE_CACHE):
        """
            HTTP post. Cached version.
        """
        if not self.__client.requests_cache().enabled():
            return self.post2(query, data)

        # TODO: Lock requests cache
        cache = self.__client.requests_cache()
        if primary_source == self.SOURCE_CACHE:
            if cache.contains_post(query, data):
                print("POST(cached) '%s' use cached result" % query)
                return cache.post(query, data)
            print("POST '%s' update cache" % query)
            r = self.post2(query, data)
            if r.status_code != self.HTTP_OK:
                return r
        elif primary_source == self.SOURCE_ORIGIN:
            print("POST '%s' update cache" % query)
            r = self.post2(query, data)
            if r.status_code != self.HTTP_OK:
                if not cache.contains_post(query, data):
                    return r
                print("POST(cached) '%s' use cached result" % query)
                return cache.post(query, data)

        return cache.update_post(query, data, r)

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
        ret = []
        for version in self.metadata_for(query).versions_for(query):
            for sq in self.__client.simple_queries_for(query, version):
                for asset in self.perform_aql(sq.to_aql_query()):
                    ret.append(asset)
        return ret

    def download_file(self, destination_file, url):
        # TODO: Lock destination

        destination_parent_path = os.path.abspath(os.path.join(destination_file, os.pardir))
        if not os.path.isdir(destination_parent_path): os.makedirs(destination_parent_path)

        r = self.get2(url)
        if r.status_code != self.HTTP_OK:
            raise self.HttpError(r.status_code)

        with open(destination_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                f.write(chunk)

    def place_asset_into(self, destination_file, asset):
        if not self.__client.objects_cache().enabled():
            print("Download object: '%s'" % asset.url())
            self.download_file(destination_file, asset.url())
            return

        cache = self.__client.objects_cache()
        if cache.contains(asset) and cache.validate_destination(asset, destination_file):
            print("Destination is actual: '%s'" % asset.url())
            return

        if cache.contains(asset) and not cache.validate_destination(asset, destination_file):
            print("Cached object: '%s'" % asset.url())
            cache.copy_asset(asset, destination_file)
            return

        # TODO: Lock destination
        print("Download new object: '%s'" % asset.url())
        asset_path          = cache.asset_path(asset)
        temp_file           = asset_path + ".dwn"

        self.download_file(temp_file, asset.url())

        cache.move_file(temp_file, asset_path)
        cache.copy_asset(asset, destination_file)
