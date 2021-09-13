import utils

import metadata_versioning

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
        doc = utils.XmlUtils.parse(input_string)
        self = Metadata()
        self.__groupId      = utils.XmlUtils.get_value_by_path(doc.documentElement, "/groupId")
        self.__artifactId   = utils.XmlUtils.get_value_by_path(doc.documentElement, "/artifactId")
        self.__version      = utils.XmlUtils.get_value_by_path(doc.documentElement, "/version")

        versioning          = utils.XmlUtils.get_item_by_path(doc.documentElement, "/versioning")
        self.__versioning   = metadata_versioning.MetadataVersioning.from_element(versioning)

        return self


    def versions_for(self, query):
        # TODO:
        return self.__versioning.versions()
