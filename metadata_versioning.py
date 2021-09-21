from xml_utils import XmlUtils

class MetadataVersioning:
    def __init__(self):
        self.__latest       = None
        self.__release      = None
        self.__versions     = []
        self.__lastUpdated  = None

    def print(self):
        print("latest: %s" % self.__latest)
        print("release: %s" % self.__release)
        print("lastUpdated: %s" % self.__lastUpdated)
        for version in self.__versions:
            print("\tversion: %s" % version)

    @staticmethod
    def from_element(element):
        self = MetadataVersioning()
        self.__latest       = XmlUtils.get_value_by_path(element, "/latest")
        self.__release      = XmlUtils.get_value_by_path(element, "/release")
        self.__lastUpdated  = XmlUtils.get_value_by_path(element, "/lastUpdated")
        elements = element.getElementsByTagName("version")
        for element in elements:
            self.__versions.append(element.firstChild.wholeText)

        return self

    def versions(self):
        return self.__versions
