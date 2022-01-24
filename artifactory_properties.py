import os

from artifactory_requests import ArtifactoryRequests

class ArtifactoryProperties:
    GAVC_SERVER_URL_ENV             = "GAVC_SERVER_URL"
    GAVC_SERVER_REPOSITORY_ENV      = "GAVC_SERVER_REPOSITORY"
    GAVC_SERVER_API_ACCESS_TOKEN_ENV= "GAVC_SERVER_API_ACCESS_TOKEN"

    TOKEN_HDR       = "X-JFrog-Art-Api"
    DETAILS_HDR     = "X-Result-Detail"
    DETAILS_VALUE   = "info, properties"

    AQL_SUFFIX      = "api/search/aql"

    def __make_headers(self):
        self.__headers = {
            self.TOKEN_HDR:     self.__token,
            self.DETAILS_HDR:   self.DETAILS_VALUE,
        }

    def __make_requests(self):
        self.__requests = ArtifactoryRequests(self)

    def __init__(self, url, repo, token):
        self.__url      = url
        self.__repo     = repo
        self.__token    = token
        self.__make_headers()
        self.__make_requests()

    @staticmethod
    def from_env(def_url = None, def_repo = None, def_token = None):
        url     = os.environ.get(ArtifactoryProperties.GAVC_SERVER_URL_ENV, def_url)
        repo    = os.environ.get(ArtifactoryProperties.GAVC_SERVER_REPOSITORY_ENV, def_repo)
        token   = os.environ.get(ArtifactoryProperties.GAVC_SERVER_API_ACCESS_TOKEN_ENV, def_token)
        return ArtifactoryProperties(url, repo, token)

    def url(self):
        return self.__url

    def repository_metadata_path(self, metadata_path):
        return "%s/%s" % (self.__repo, metadata_path)

    def repository_metadata_url(self, metadata_path):
        return "%s/%s" % (self.__url, self.repository_metadata_path(metadata_path))

    def aql_url(self):
        return "%s/%s" % (self.__url, self.AQL_SUFFIX)

    def repository(self):
        return self.__repo

    def token(self):
        return self.__token

    def headers(self):
        return self.__headers

    def requests(self):
        return self.__requests

    def simple_queries_for(self, query, version):
        return query.simple_queries_for(self.__repo, version)
