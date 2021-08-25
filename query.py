import lark
import simple_query
import lark_utils


class Query:
    GRAMMAR = """
        start: group ":" name ( ":" version ( ":" cel )? )?
        group: /[0-9a-zA-Z\.\-\_]+/
        name: /[0-9a-zA-Z\_]+/
        version:  /[0-9a-zA-Z\.\-\_\*\+\[\]\(\)\,]+/
        ce: classifier ( "@" extenstion)? ","?
        cel: ce+
        classifier: /[0-9a-zA-Z\.\-\_]+/
        extenstion: /[0-9a-zA-Z\_]+/
    """

    def __init__(self, group = None, name = None, version = None, classifiers = []):
        self.__group        = group
        self.__name         = name
        self.__version      = version
        self.__classifiers  = classifiers

    @staticmethod
    def parse(input_string):
        tree = lark_utils.TreeHelper(lark.Lark(Query.GRAMMAR, parser='lalr').parse(input_string))
        self = Query()

        self.__group = tree.tree_by_path("group").first_value()
        self.__name =  tree.tree_by_path("name").first_value()

        if len(tree) < 3:
            return self

        self.__version = tree.tree_by_path("version").first_value()

        if len(tree) < 4:
            return self

        for ce in tree.tree_by_path("cel").children():
            classifier = ce.tree_by_path("classifier").first_value()
            ext_tree = ce.tree_by_path("extenstion")
            if ext_tree:
                extenstion = ext_tree.first_value()
            else:
                extenstion = None
            self.__classifiers.append((classifier, extenstion))

        return self

    def __str__(self):
        ret = "%s:%s" % (self.__group, self.__name)
        if not self.__version:
            return ret

        ret = ":%s" % self.__version

        if self.__classifiers:
            sepa = ":"
            for c in self.__classifiers:
                ret += "%s%s" % (sepa, c[0])
                if c[1]:
                    ret += "@%s" % c[1]
                sepa = ","

        return ret

    def __group_path(self):
        if not self.__group: return None

        return self.__group.replace('.', '/')

    def metadata_path(self):
        return "%s/%s/%s" % (self.__group_path(), self.__name, "maven-metadata.xml")

    def _aql_path(self):
        return "%s/%s/*" % (self.__group_path(), self.__name )

    def simple_queries_for(self, repo, version):
        if not self.__classifiers:
            return ( simple_query.SimpleQuery(self, repo, self.__group, self.__name, version) )
        else:
            return ( simple_query.SimpleQuery(self, repo, self.__group, self.__name, version, classifier[0], classifier[1]) for classifier in self.__classifiers )


if __name__ == "__main__":
    q = Query.parse("1.re:2")
    print(q)
    print(q.metadata_path())
    q = Query.parse("1:2:3")
    print(q)
    print(q.metadata_path())
    q = Query.parse("1:2:3:4")
    print(q)
    print(q.metadata_path())
    q = Query.parse("1:2:3:4@ext,5@ext")
    print(q)
    print(q.metadata_path())
