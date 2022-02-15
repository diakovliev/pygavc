import lark

from .simple_query import SimpleQuery
from .lark_utils import TreeHelper
from .version import VersionData
from .pom import Pom

class Query:
    GRAMMAR = """
        start: group ":" name ( ":" version ( ":" cel? )? )?
        ce: ( classifier ( "@" extension )? ) | ( "@" extension ) ","?
        cel: ce+
        group: /[0-9a-zA-Z\.\-\_]+/
        name: /[0-9a-zA-Z\_]+/
        version:  /[0-9a-zA-Z\.\-\_\*\+\[\]\(\)\,]+/
        classifier: /[0-9a-zA-Z\.\-\_]+/
        extension: /[0-9a-zA-Z\_]+/
    """

    MAVEN_METADATA_XML = "maven-metadata.xml"

    def __init__(self, group = None, name = None, version = None, classifiers = None):
        self.__group        = group
        self.__name         = name
        self.__version      = version
        self.__classifiers  = classifiers

    def make_subquery(self, **kwargs):
        group       = self.__group
        name        = self.__name
        version     = self.__version
        classifiers = self.__classifiers
        extension   = ""
        if "version" in kwargs:
            version = VersionData.parse(kwargs.get("version"))
        if "extension" in kwargs:
            extenstion = kwargs.get("extenstion")
        if "classifier" in kwargs:
            classifiers = [ (kwargs.get("classifier"), extension) ]
        return Query(group, name, version, classifiers)

    def pom(self):
        return Pom(self.__group, self.__name, str(self.__version))

    def set_version(self, version):
        self.__version = VersionData.parse(version)

    @staticmethod
    def parse(input_string):
        tree = TreeHelper(lark.Lark(Query.GRAMMAR, parser='lalr').parse(input_string))
        self = Query()

        self.__group = tree.tree_by_path("group").first_value()
        self.__name =  tree.tree_by_path("name").first_value()

        if len(tree) < 3:
            return self

        self.__version = VersionData.parse(tree.tree_by_path("version").first_value())

        if len(tree) < 4:
            return self

        self.__classifiers = list()
        for ce in tree.tree_by_path("cel").children():
            classifier_tree = ce.tree_by_path("classifier")
            if classifier_tree:
                classifier = classifier_tree.first_value()
            else:
                classifier = None
            ext_tree = ce.tree_by_path("extension")
            if ext_tree:
                extension = ext_tree.first_value()
            else:
                extension = None
            self.__classifiers.append((classifier, extension))

        return self

    def __str__(self):
        ret = "%s:%s" % (self.__group, self.__name)
        if not self.__version:
            return ret

        ret += ":%s" % str(self.__version)

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

    def artifact_path(self):
        return "%s/%s" % (self.__group_path(), self.__name)

    def version_path(self, version = None):
        if version:
            return "%s/%s" % (self.artifact_path(), version)
        else:
            assert self.__version is not None
            return "%s/%s" % (self.artifact_path(), str(self.__version))

    def metadata_path(self):
        return "%s/%s" % (self.artifact_path(), self.MAVEN_METADATA_XML)

    def object_path(self, classifier, extension):
        object_path = "%s/%s-%s" % (self.version_path(), self.__name, str(self.__version))
        if classifier:
            object_path += "-%s" % classifier
        if extension:
            object_path += ".%s" % extension
        return object_path

    def pom_path(self):
        return self.object_path(None, "pom")

    def version(self):
        return self.__version

    def _aql_path(self):
        return "%s/*" % self.artifact_path()

    def simple_queries_for(self, repo, version):
        if self.__classifiers:
            for classifier, extension in self.__classifiers:
                yield SimpleQuery(self, repo, self.__group, self.__name, version, classifier, extension)
        else:
            yield SimpleQuery(self, repo, self.__group, self.__name, version)


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
