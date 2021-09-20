import unittest
import lark_utils
import lark

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

    def test_tree(self):
        tree_helper = lark_utils.TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        self.assertEqual(type(tree_helper), lark_utils.TreeHelper)
        self.assertEqual(type(tree_helper.tree()), lark.tree.Tree)

    def test_tree_by_path(self):
        tree_helper = lark_utils.TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        self.assertEqual(type(tree_helper.tree_by_path("cel")), lark_utils.TreeHelper)
        self.assertEqual(type(tree_helper.tree_by_path("version")), lark_utils.TreeHelper)
        self.assertEqual(type(tree_helper.tree_by_path("cel/ce/extension")), lark_utils.TreeHelper)
        self.assertNotEqual(type(tree_helper.tree_by_path("abcd")), lark_utils.TreeHelper)

    def test_children(self):
        tree_helper = lark_utils.TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        test_list = []
        for ce in tree_helper.tree_by_path("cel").children():
            test_list.append(ce)
        self.assertEqual(len(test_list), 2)

    def test_first_value(self):
        tree_helper = lark_utils.TreeHelper(lark.Lark(LarkUtilsTests.GRAMMAR, parser='lalr').parse(LarkUtilsTests.TEST_STRING))
        self.assertEqual(tree_helper.tree_by_path("name").first_value(), "2")
        self.assertEqual(tree_helper.tree_by_path("cel").first_value(), None)
        self.assertEqual(tree_helper.tree_by_path("cel").first_value(1037), 1037)

if __name__ == "__main__":
    unittest.main()
