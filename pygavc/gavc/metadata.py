from .xml_utils import XmlUtils
from .versions_filter import VersionsFilter
from .metadata_versioning import MetadataVersioning

class Metadata:

    def __init__(self):
        self.__groupId      = None
        self.__artifactId   = None
        self.__version      = None
        self.__versioning   = None


    def print(self):
        print("groupId: %s" % self.__groupId)
        print("artifactId: %s" % self.__artifactId)
        print("version: %s" % self.__version)
        self.__versioning.print()


    @staticmethod
    def parse(input_string):
        doc = XmlUtils.parse(input_string)
        self = Metadata()
        self.__groupId      = XmlUtils.get_value_by_path(doc.documentElement, "/groupId")
        self.__artifactId   = XmlUtils.get_value_by_path(doc.documentElement, "/artifactId")
        self.__version      = XmlUtils.get_value_by_path(doc.documentElement, "/version")

        versioning          = XmlUtils.get_item_by_path(doc.documentElement, "/versioning")
        self.__versioning   = MetadataVersioning.from_element(versioning)

        return self


    def versions_for(self, query):
        vfilter = VersionsFilter(query.version())
        return vfilter.filtered(self.__versioning.versions())
