import os

from .gavc_parameters import GavcClientBaseParamsHandler, GavcClientParamsHandler
from .client_cache import ClientCache
from .artifactory_requests import ArtifactoryRequests


class ArtifactoryClient(object):
    TOKEN_HDR       = "X-JFrog-Art-Api"
    DETAILS_HDR     = "X-Result-Detail"
    DETAILS_VALUE   = "info, properties"

    AQL_SUFFIX      = "api/search/aql"

    GET_LOCAL_REPOS = "api/repositories?type=local"

    def __make_headers(self):
        self.__headers = {
            self.TOKEN_HDR:     self.token(),
            self.DETAILS_HDR:   self.DETAILS_VALUE,
        }

    def __make_requests(self):
        self.__requests = ArtifactoryRequests(self)

    def __init__(self, cache, server = None, repository = None, token = None):

        self.__server       = server
        self.__repository   = repository
        self.__token        = token

        self.__cache        = cache
        self.__make_headers()
        self.__make_requests()

    @staticmethod
    def from_params_handler(params_handler = GavcClientParamsHandler()):
        params_handler.print_all_params(" - Artifactory client parameters:")

        server          = params_handler.get_param(GavcClientBaseParamsHandler.SERVER_PARAM)
        repository      = params_handler.get_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM)
        token           = params_handler.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM)

        cache           = ClientCache.from_params_handler(params_handler)

        return ArtifactoryClient(cache, server, repository, token)

    def url(self):
        return self.__server

    def repository(self):
        return self.__repository

    def token(self):
        return self.__token

    def repository_path(self, object_path):
        return "%s/%s" % (self.repository(), object_path)

    def repository_url(self, object_path):
        return "%s/%s" % (self.url(), self.repository_path(object_path))

    def aql_url(self):
        return "%s/%s" % (self.url(), self.AQL_SUFFIX)

    def get_local_repos_request(self):
        return "%s/%s" % (self.url(), self.GET_LOCAL_REPOS)

    def headers(self):
        return self.__headers

    def requests(self):
        return self.__requests

    def cache(self):
        return self.__cache

    def resolved_queries_for(self, query, version):
        return query.resolved_queries_for(self.repository(), version)
