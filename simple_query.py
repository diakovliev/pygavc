import json


class SimpleQuery:
    def __init__(self, parent, repo, group = None, name = None, version = None, classifier = None, extension = None):
        self.__parent       = parent
        self.__repo         = repo
        self.__group        = group
        self.__name         = name
        self.__version      = version
        self.__classifier   = classifier
        self.__extension    = extension

    def __aql_name_condition(self):

        base = "%s-%s" % (self.__name, self.__version)
        if self.__classifier:
            name = "%s-%s" % (base, self.__classifier)
            if self.__extension:
                name = "%s.%s" % (name, self.__extension)
            else:
                name = "%s.*" % name
        else:
            name += "*"

        return { "$match": name }

    def __aql_cond(self):
        aql = {
            "$and": [
                { "repo": self.__repo },
                { "path": {
                        "$match": self.__parent._aql_path(),
                    }
                },
                { "name": self.__aql_name_condition() }
            ]
        }
        return json.dumps(aql)


    def to_aql_query(self):
        return "items.find(%s).include(\"*\")" % self.__aql_cond()
