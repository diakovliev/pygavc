import argparse
import os
import shutil

from gavc.query import Query
from gavc.artifactory_client import ArtifactoryClient

################################################################################
class Downloader:
    def __init__(self, client):
        self.__client = client

    def perform(self, query, output):
        for asset in  self.__client.requests().assets_for(query):
            destination_file = output if output else os.path.join(os.getcwd(), asset.name())
            self.__client.requests().retrieve_asset(asset, destination_file)

################################################################################
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        action="store",
        help="Output file."
    )

    parser.add_argument(
        "target",
        nargs=1,
        help="Gavc target."
    )

    args = parser.parse_args()

    print(" - Gavc: %s" % args.target)
    print(" - Output: %s" % args.output)

    downloader = Downloader(ArtifactoryClient())

    query = Query.parse(args.target[0])

    downloader.perform(query, args.output)

################################################################################
if __name__ == "__main__":
    main()
