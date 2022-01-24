import xml.etree.ElementTree as et


class Pom:
    ELEMENT_PROJECT         = 'project'
    ELEMENT_MODEL_VERSION   = 'modelVersion'
    MODEL_VERSION           = '4.0.0'
    ELEMENT_GROUP_ID        = 'groupId'
    ELEMENT_ARTIFACT_ID     = 'artifactId'
    ELEMENT_VERSION         = 'version'
    ELEMENT_PACKAGING       = 'packaging'
    PACKAGING               = 'pom'

    def __init__(self, groupId, artifactId, version):
        self.__groupId      = groupId
        self.__artifactId   = artifactId
        self.__version      = version
        self.__createProject()

    def __createSubElements(self, elements):
        for element, text in elements.items():
            subElement = et.SubElement(self.__project, element)
            subElement.text = text

    def __createProject(self):
        self.__project = et.Element(self.ELEMENT_PROJECT)
        self.__createSubElements({
            self.ELEMENT_MODEL_VERSION: self.MODEL_VERSION,
            self.ELEMENT_PACKAGING: self.PACKAGING,
            self.ELEMENT_GROUP_ID: self.__groupId,
            self.ELEMENT_ARTIFACT_ID: self.__artifactId,
            self.ELEMENT_VERSION: self.__version,
        })

    def tobytes(self):
        return et.tostring(self.__project)

    def tostring(self):
        return self.tobytes().decode('utf-8')


if __name__ == "__main__":
    print("%s" % Pom("group", "artifact", "0.1.2").tostring())
