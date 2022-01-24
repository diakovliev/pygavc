import requests

class ArtifactoryRequests:
    def __init__(self, properties):
        self.__props = properties
        self.__session = requests.Session()

    def get(self, query):
        return self.__session.get(query, headers=self.__props.headers())

    def post(self, query, data = None):
        return self.__session.post(query, headers=self.__props.headers(), data=data)

    def metadata_for(self, query):
        metadata_url = self.__props.repository_metadata_url(query.metadata_path())
        return self.get(metadata_url)

    def perform_aql(self, aql):
        return self.post(self.__props.aql_url(), aql)
