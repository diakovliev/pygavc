import os
import requests

import query

import metadata


class Connection:
    TOKEN_HDR       = "X-JFrog-Art-Api"
    DETAILS_HDR     = "X-Result-Detail"
    DETAILS_VALUE   = "info, properties"

    AQL_SUFFIX      = "api/search/aql"

    def __init__(self, server, repository, api_token):
        self.__server       = server
        self.__repository   = repository
        self.__api_token    = api_token

    def perform(self, query) -> metadata.Metadata:

        headers = {
            self.TOKEN_HDR:     self.__api_token,
            self.DETAILS_HDR:   self.DETAILS_VALUE,
        }

        metadata_url = "%s/%s/%s" % (self.__server, self.__repository, query.metadata_path())

        print(metadata_url)
        r = requests.get(metadata_url, headers=headers)
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

            sq = query.simple_queries_for(self.__repository, version)
            for q in sq:

                aql = q.to_aql_query()

                print("aql: %s" % aql)

                aql_uri = "%s/%s" % (self.__server, self.AQL_SUFFIX)

                print("aql uri: %s", aql_uri)

                r = requests.post(aql_uri, headers=headers, data=aql)
                if r.status_code != 200:
                    print("ERROR (%s)" % r.status_code)
                    return None
                else:
                    print("OK")
                    print(r.text)

        return mm



def main():
    token = os.environ["GAVC_SERVER_API_ACCESS_TOKEN"]
    url = os.environ["GAVC_SERVER_URL"]
    repo = os.environ["GAVC_SERVER_REPOSITORY"]

    c = Connection(url, repo, token)

    q = query.Query.parse("entone.sdk.release:mipsel_linux:*[20,22]:oemsdk_release@zip,oemsdk_debug@zip")
    c.perform(q)

    q = query.Query.parse("charter.worldbox11.oemsdk.release:humaxwb11:15.4.+")
    c.perform(q)

if __name__ == "__main__":
    main()
