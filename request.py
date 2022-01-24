import os
import sys
import shutil

import query
import metadata

from simple_query import AqlResults
from artifactory_properties import ArtifactoryProperties

class Connection:

    def __init__(self, properties):
        self.__props        = properties


    def perform(self, query, download = False):

        r = self.__props.requests().metadata_for(query)
        if r.status_code != 200:
            print("ERROR (%s)" % r.status_code)
            return None
        else:
            print("OK")
            print(r.text)

        mm = metadata.Metadata.parse(r.text)
        mm.print()

        versions = mm.versions_for(query)
        for version in versions:
            print("process version: %s" % version)

            if download:
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

            sq = self.__props.simple_queries_for(query, version)
            for q in sq:

                aql = q.to_aql_query()

                print("aql: %s" % aql)

                r = self.__props.requests().perform_aql(aql)
                if r.status_code != 200:
                    print("ERROR (%s)" % r.status_code)
                    return None
                else:
                    print("http OK")
                    print(r.text)
                    if download:
                        aql_results = AqlResults.parse(r.text, self.__props.url())
                        for obj in aql_results:
                            sys.stdout.write("Downloading '%s' " % obj.url())
                            sys.stdout.flush()
                            r = self.__props.requests().get(obj.url())
                            if r.status_code != 200:
                                print("ERROR (%s)" % r.status_code)
                            else:
                                with open(os.path.join(directory, obj.name()), 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=1024*1024):
                                        f.write(chunk)
                                        sys.stdout.write(".")
                                        sys.stdout.flush()
                                sys.stdout.write(" OK")
                                sys.stdout.flush()
                                print("")

        return mm



def main():
    c = Connection(ArtifactoryProperties.from_env())

    q = query.Query.parse("entone.sdk.release:mipsel_linux:*[20,22]:oemsdk_release@zip,oemsdk_debug@zip")
    c.perform(q)

    q = query.Query.parse("charter.worldbox11.oemsdk.release:humaxwb11:15.4.+")
    c.perform(q, True)

if __name__ == "__main__":
    main()
