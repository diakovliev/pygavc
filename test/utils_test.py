import unittest
import lark
import xml

from gavc.lark_utils import TreeHelper
from gavc.xml_utils import XmlUtils

class LarkUtilsTests(unittest.TestCase):

    GRAMMAR = """
        start: group ":" name ( ":" version ( ":" cel )? )?
        group: /[0-9a-zA-Z\.\-\_]+/
        name: /[0-9a-zA-Z\_]+/
        version:  /[0-9a-zA-Z\.\-\_\*\+\[\]\(\)\,]+/
        ce: classifier ( "@" extension)? ","?
        cel: ce+
        classifier: /[0-9a-zA-Z\.\-\_]+/
        extension: /[0-9a-zA-Z\_]+/
    """

    TEST_STRING = "1:2:3:4@ext,5@3ext"

    TEST_DEFAULT_VALUE = 1037

    def test_tree(self):
        tree_helper = TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        self.assertEqual(type(tree_helper), TreeHelper)
        self.assertEqual(type(tree_helper.tree()), lark.tree.Tree)

    def test_tree_by_path(self):
        tree_helper = TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        self.assertEqual(type(tree_helper.tree_by_path("cel")), TreeHelper)
        self.assertEqual(type(tree_helper.tree_by_path("version")), TreeHelper)
        self.assertEqual(type(tree_helper.tree_by_path("cel/ce/extension")), TreeHelper)
        self.assertNotEqual(type(tree_helper.tree_by_path("abcd")), TreeHelper)

    def test_children(self):
        tree_helper = TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        test_list = []
        for ce in tree_helper.tree_by_path("cel").children():
            test_list.append(ce)
        self.assertEqual(len(test_list), 2)

    def test_first_value(self):
        tree_helper = TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        self.assertEqual(tree_helper.tree_by_path("name").first_value(), "2")
        self.assertEqual(tree_helper.tree_by_path("cel").first_value(), None)
        self.assertEqual(tree_helper.tree_by_path("cel").first_value(LarkUtilsTests.TEST_DEFAULT_VALUE), LarkUtilsTests.TEST_DEFAULT_VALUE)

class XmlUtilsTests(unittest.TestCase):

    TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
                  <metadata modelVersion="1.1.0">
                    <test id="1037">Ashen One</test>
                    <groupId>adk.trunk</groupId>
                    <artifactId>adk</artifactId>
                    <version>63</version>
                    <versioning>
                      <latest>61</latest>
                      <release>62</release>
                      <versions>
                        <version>45</version>
                        <version>46</version>
                      </versions>
                      <lastUpdated>20171211011023</lastUpdated>
                    </versioning>
                  </metadata>"""

    TEST_DEFAULT_VALUE = 1037

    def test_parse(self):
        self.assertEqual(type(XmlUtils.parse(XmlUtilsTests.TEST_XML)), xml.dom.minidom.Document)

    def test_createxmldoc(self):
        self.assertEqual(type(XmlUtils.createxmldoc(XmlUtilsTests.TEST_XML)), xml.dom.minidom.Document)

    def test_get_first_item(self):
        doc = XmlUtils.parse(XmlUtilsTests.TEST_XML)
        self.assertEqual(type(XmlUtils.get_first_item(doc.documentElement, "versioning")), xml.dom.minidom.Element)
        self.assertEqual(XmlUtils.get_first_item(doc.documentElement, "huh"), None)

    def test_get_first_item_whole_text(self):
        doc = XmlUtils.parse(XmlUtilsTests.TEST_XML)
        self.assertEqual(XmlUtils.get_first_item_whole_text(doc.documentElement, "artifactId"), "adk")
        self.assertEqual(XmlUtils.get_first_item_whole_text(doc.documentElement, "test"), "Ashen One")
        self.assertEqual(XmlUtils.get_first_item_whole_text(doc.documentElement, "heh"), None)
        self.assertEqual(XmlUtils.get_first_item_whole_text(doc.documentElement, "heh", XmlUtilsTests.TEST_DEFAULT_VALUE), XmlUtilsTests.TEST_DEFAULT_VALUE)

    def test_get_attr_value(self):
        doc = XmlUtils.parse(XmlUtilsTests.TEST_XML)
        test_element = XmlUtils.get_first_item(doc.documentElement, "test")
        self.assertEqual(XmlUtils.get_attr_value(test_element, "id"), "1037")
        self.assertEqual(XmlUtils.get_attr_value(test_element, "di"), None)
        self.assertEqual(XmlUtils.get_attr_value(test_element, "di", XmlUtilsTests.TEST_DEFAULT_VALUE), XmlUtilsTests.TEST_DEFAULT_VALUE)

    def test_get_item_by_path(self):
        doc = XmlUtils.parse(XmlUtilsTests.TEST_XML)
        self.assertEqual(type(XmlUtils.get_item_by_path(doc.documentElement, "/versioning")), xml.dom.minidom.Element)
        self.assertEqual(type(XmlUtils.get_item_by_path(doc.documentElement, "/versioning/versions/version")), xml.dom.minidom.Element)
        self.assertEqual(XmlUtils.get_item_by_path(doc.documentElement, "/hola"), None)
        self.assertEqual(XmlUtils.get_item_by_path(doc.documentElement, "/hola", XmlUtilsTests.TEST_DEFAULT_VALUE), XmlUtilsTests.TEST_DEFAULT_VALUE)

    def test_get_value_by_path(self):
        doc = XmlUtils.parse(XmlUtilsTests.TEST_XML)
        self.assertEqual(XmlUtils.get_value_by_path(doc.documentElement, "/versioning/lastUpdated"), "20171211011023")
        self.assertEqual(XmlUtils.get_value_by_path(doc.documentElement, "/hola"), None)
        self.assertEqual(XmlUtils.get_value_by_path(doc.documentElement, "/hola", XmlUtilsTests.TEST_DEFAULT_VALUE), XmlUtilsTests.TEST_DEFAULT_VALUE)

if __name__ == "__main__":
    unittest.main()
