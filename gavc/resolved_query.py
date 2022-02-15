import json


class ResolvedQuery:
    def __init__(self, parent, repo, group = None, name = None, version = None, classifier = None, extension = None):
        self.__parent       = parent
        self.__repo         = repo
        self.__group        = group
        self.__name         = name
        self.__version      = version
        self.__classifier   = classifier
        self.__extension    = extension

    def __aql_name_condition(self, root_elements = False):
        append_star = not self.__classifier or not self.__extension
        name = "%s-%s" % (self.__name, self.__version)

        if self.__classifier:
            name = "%s-%s" % (name, self.__classifier)

        if self.__extension:
            name = "%s.%s" % (name, self.__extension)
            append_star = False

        if append_star and root_elements:
            name = "%s.*" % name
        elif append_star and not root_elements:
            name = "%s-*" % name

        return { "$match": name }

    def __aql_cond(self):
        aql = {
            "$or": [
                {
                    "$and": [
                        { "repo": self.__repo },
                        { "path": {
                                "$match": self.__parent._aql_path(),
                            }
                        },
                        { "name": self.__aql_name_condition(True) }
                    ]
                },
                {
                    "$and": [
                        { "repo": self.__repo },
                        { "path": {
                                "$match": self.__parent._aql_path(),
                            }
                        },
                        { "name": self.__aql_name_condition(False) }
                    ]
                },
            ]
        }
        return json.dumps(aql)

    def to_aql_query(self):
        return "items.find(%s).include(\"*\")" % self.__aql_cond()
