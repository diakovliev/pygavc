import copy

from xml.dom import minidom

################################################################################
class XmlUtils:
    PATH_SEPA = '/'
    ATTR_SEPA = '@'

    @staticmethod
    def parse(input_obj):
        return minidom.parseString(input_obj)

    @staticmethod
    def createxmldoc(roottag):
        return minidom.getDOMImplementation().createDocument(None, roottag, None)

    @staticmethod
    def get_first_item(xml_element, tag_name, default = None):
        if not xml_element:
            return default

        elements = xml_element.getElementsByTagName(tag_name)
        if not len(elements):
            return default

        return elements[0]

    @staticmethod
    def get_first_item_whole_text(xml_element, tag_name, default = None):
        firstChild = XmlUtils.get_first_item(xml_element, tag_name).firstChild
        if firstChild and firstChild.wholeText:
            return firstChild.wholeText
        else:
            return default

    @staticmethod
    def get_attr_value(xml_element, attr_name, default = None):
        if not xml_element:
            return default

        attr = xml_element.attributes[attr_name]
        if attr and attr.value:
            return attr.value
        else:
            return default

    @staticmethod
    def get_by_path(xml_element, in_path, default = None, no_extract_values = False):

        if XmlUtils.ATTR_SEPA in in_path:
            path, attr  = in_path.split(XmlUtils.ATTR_SEPA, 1)
        else:
            path = in_path
            attr = None

        path_parts  = list(filter(lambda x: x, path.split(XmlUtils.PATH_SEPA)))

        queue       = copy.copy(path_parts)

        curr        = xml_element
        curr_path   = ''

        while queue:
            tag = queue.pop(0)
            curr_path += tag

            childs = curr.getElementsByTagName(tag)

            if not childs:
                return default

            curr_path += XmlUtils.PATH_SEPA
            curr = childs[0]

        ret = curr

        if not no_extract_values:
            if not attr and curr.firstChild and curr.firstChild.wholeText:
                ret = curr.firstChild.wholeText
            elif attr:
                ret = XmlUtils.get_attr_value(curr, attr, default)

        return ret
