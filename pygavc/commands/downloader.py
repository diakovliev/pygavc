import os

from ..gavc.query import Query
from ..gavc.artifactory_client import ArtifactoryClient



################################################################################
class Downloader:
    def __init__(self, target):
        self.__target = target

    def __call__(self, output):

        client = ArtifactoryClient.from_params_handler()

        query = Query.parse(self.__target)

        for asset in client.requests().assets_for(query):
            destination_file = output if output else os.path.join(os.getcwd(), asset.name())
            client.requests().retrieve_asset(asset, destination_file)
