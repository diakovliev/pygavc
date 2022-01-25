import os

from parameters import BaseParamsHandler
from parameters import GavcClientParamsHandler
from artifactory_requests import ArtifactoryRequests
from artifactory_requests_cache import ArtifactoryRequestsCache
from artifactory_objects_cache import ArtifactoryObjectsCache


class ArtifactoryClient(GavcClientParamsHandler):
    TOKEN_HDR       = "X-JFrog-Art-Api"
    DETAILS_HDR     = "X-Result-Detail"
    DETAILS_VALUE   = "info, properties"

    AQL_SUFFIX      = "api/search/aql"

    def __make_headers(self):
        self.__headers = {
            self.TOKEN_HDR:     self.token(),
            self.DETAILS_HDR:   self.DETAILS_VALUE,
        }

    def __init_requests_cache(self):
        self.__requests_cache = ArtifactoryRequestsCache(self)

    def __init_objects_cache(self):
        self.__objects_cache = ArtifactoryObjectsCache(self)

    def __make_requests(self):
        self.__requests = ArtifactoryRequests(self)

    def __init__(self):
        GavcClientParamsHandler.__init__(self)
        self.__init_objects_cache()
        self.__init_requests_cache()
        self.__make_headers()
        self.__make_requests()

    def url(self):
        return self.get_param(BaseParamsHandler.SERVER_PARAM)

    def repository_metadata_path(self, metadata_path):
        return "%s/%s" % (self.repository(), metadata_path)

    def repository_metadata_url(self, metadata_path):
        return "%s/%s" % (self.url(), self.repository_metadata_path(metadata_path))

    def aql_url(self):
        return "%s/%s" % (self.url(), self.AQL_SUFFIX)

    def repository(self):
        return self.get_param(BaseParamsHandler.REPOSITORY_PARAM)

    def token(self):
        return self.get_param(BaseParamsHandler.TOKEN_PARAM)

    def headers(self):
        return self.__headers

    def requests(self):
        return self.__requests

    def requests_cache(self):
        return self.__requests_cache

    def objects_cache(self):
        return self.__objects_cache

    def simple_queries_for(self, query, version):
        return query.simple_queries_for(self.repository(), version)
