import json
import lark
from lark import Lark, Transformer

class AqlObject:

    def __init__(self, data = None):
        self.__data = data

    def name(self):
        return self.__data["name"]

    def type(self):
        return self.__data["type"]

    def size(self):
        return self.__data["size"]

    def md5(self):
        return self.__data["actual_md5"]

    def sha1(self):
        return self.__data["actual_sha1"]

    def url(self):
        return self.__data["server"] + "/" + self.__data["repo"] + "/" + self.__data["path"] + "/" + self.__data["name"]

    def __str__(self):
        result = self.type() + "\n"
        result += self.name() + "\n"
        result += "size: " + str(self.size()) + "\n"
        result += "md5: " + str(self.md5()) + "\n"
        result += "sha1: " + str(self.sha1()) + "\n"
        result += "created: " + self.__data["created"] + "\n"
        result += "url: " + self.url() + "\n"
        return result

class AqlResults:

    GRAMMAR = r"""
        ?value: dict
              | list
              | string
              | SIGNED_NUMBER      -> number
              | "true"             -> true
              | "false"            -> false
              | "null"             -> null

        list : "[" [value ("," value)*] "]"

        dict : "{" [pair ("," pair)*] "}"
        pair : string ":" value

        string : ESCAPED_STRING

        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        %import common.WS
        %ignore WS
        """

    def __init__(self):
        self.__objects = None

    @staticmethod
    def parse(input_string, server_url):
        try:
            tree = Lark(AqlResults.GRAMMAR, parser='lalr', start='value').parse(input_string)
            aql_results = _AqlResultsTransformer().transform(tree)
            return [ AqlObject(dict(obj, server = server_url)) for obj in aql_results["results"] ]
        except TypeError:
            return None
        except lark.exceptions.UnexpectedToken:
            return None

class _AqlResultsTransformer(Transformer):
    def string(self, s):
        (s,) = s
        return s[1:-1]

    def number(self, n):
        (n,) = n
        return int(n)

    list = list
    pair = tuple
    dict = dict

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False

class SimpleQuery:
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
