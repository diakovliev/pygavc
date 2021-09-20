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
    def get_item_by_path(xml_element, in_path, default = None):
        path_parts  = list(filter(lambda x: x, in_path.split(XmlUtils.PATH_SEPA)))

        curr        = xml_element
        curr_path   = ''

        while path_parts:
            tag = path_parts.pop(0)
            curr_path += tag

            children = curr.getElementsByTagName(tag)

            if not children:
                return default

            curr_path += XmlUtils.PATH_SEPA
            curr = children[0]

        return curr

    @staticmethod
    def get_value_by_path(xml_element, in_path, default = None):
        if XmlUtils.ATTR_SEPA in in_path:
            path, attr  = in_path.split(XmlUtils.ATTR_SEPA, 1)
        else:
            path = in_path
            attr = None

        item = XmlUtils.get_item_by_path(xml_element, path, default)
        if not item:
            return default

        ret = default

        if not attr and item.firstChild and item.firstChild.wholeText:
            ret = item.firstChild.wholeText
        elif attr:
            ret = XmlUtils.get_attr_value(item, attr, default)

        return ret
