import os
import shutil

from gavc.query import Query
from gavc.artifactory_client import ArtifactoryClient

class Downloader:

    def __init__(self, client):
        self.__client = client


    def perform(self, query):

        directory = "./request_downloads"
        try:
            shutil.rmtree(directory)
        except OSError as e:
            pass

        try:
            os.mkdir(directory)
        except OSError as e:
            print("Error: %s : %s" % (directory, e.strerror))
            return None

        for asset in  self.__client.requests().assets_for(query):

            destination_file = os.path.join(directory, asset.name())

            self.__client.requests().place_asset_into(destination_file, asset)


def main():

    d = Downloader(ArtifactoryClient())

    q = Query.parse("entone.sdk.release:mipsel_linux:*[20,22]:oemsdk_release@zip,oemsdk_debug@zip")
    d.perform(q)

    q = Query.parse("charter.worldbox11.oemsdk.release:humaxwb11:15.4.+")
    d.perform(q)

if __name__ == "__main__":
    main()
