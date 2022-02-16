import unittest

from ..gavc.version import Op
from ..gavc.version import Range
from ..gavc.version import Version
from ..gavc.version import VersionData


class VersionTests(unittest.TestCase):

    def setUp(self):
        self.incorrect_version_test_data = list()
        self.incorrect_version_test_data.append("")
        self.incorrect_version_test_data.append("16.")
        self.incorrect_version_test_data.append("16.2.")
        self.incorrect_version_test_data.append("16.2.++")
        self.incorrect_version_test_data.append("16.2.+-")
        self.incorrect_version_test_data.append("**.2.3")
        self.incorrect_version_test_data.append(".2.3")
        self.incorrect_version_test_data.append("1.2.3[")
        self.incorrect_version_test_data.append("1.2.3]")
        self.incorrect_version_test_data.append("1.2.*[1.2.-,1.2.+")
        self.incorrect_version_test_data.append("1.2.*1.2.-,1.2.+)")
        self.incorrect_version_test_data.append("1.2.*[1.2.-1.2.+]")

        self.single_version_test_data = list()
        self.single_version_test_data.append(("16.6.2", (Op(Op.OP_CONST, "16"),Op(Op.OP_CONST, "6"), Op(Op.OP_CONST, "2"))))
        self.single_version_test_data.append(("16.6.-", (Op(Op.OP_CONST, "16"), Op(Op.OP_CONST, "6"), Op(Op.OP_OLDEST, "-"))))
        self.single_version_test_data.append(("16.+.3", (Op(Op.OP_CONST, "16"), Op(Op.OP_LATEST, "+"), Op(Op.OP_CONST, "3"))))
        self.single_version_test_data.append(("16.+.*", (Op(Op.OP_CONST, "16"), Op(Op.OP_LATEST, "+"), Op(Op.OP_ALL, "*"))))

        self.range_version_test_data = list()
        self.range_version_test_data.append(("16.6.*[16.6.3,16.6.300]", "16.6.*", "16.6.3", "16.6.300", Range.INCLUDE_LEFT | Range.INCLUDE_RIGHT))
        self.range_version_test_data.append(("16.6.*(16.6.34,16.6.+]", "16.6.*", "16.6.34", "16.6.+", Range.INCLUDE_RIGHT))
        self.range_version_test_data.append(("16.*.*[16.2.-,16.9.+)", "16.*.*", "16.2.-", "16.9.+", Range.INCLUDE_LEFT))
        self.range_version_test_data.append(("16.*.*(16.2.-,16.9.8)", "16.*.*", "16.2.-", "16.9.8", Range.EXCLUDE_ALL))

    def test_incorrect_syntax(self):
        for item in self.incorrect_version_test_data:
            self.assertEqual(VersionData.parse(item), None)

    def test_single_version(self):
        for item in self.single_version_test_data:
            version_str, ops = item

            version_data = VersionData.parse(version_str)
            self.assertEqual(type(version_data), VersionData)
            self.assertEqual(str(version_data), version_str)
            self.assertEqual(len(version_data.version().ops()), len(ops))

            for i in range(len(ops)):
                self.assertEqual(version_data.version().ops()[i].op(), ops[i].op())
                self.assertEqual(version_data.version().ops()[i].data(), ops[i].data())

    def test_range_version(self):
        for item in self.range_version_test_data:
            version_str, version_base, version_left, version_right, range_flags = item

            version_data = VersionData.parse(version_str)
            self.assertEqual(type(version_data), VersionData)
            self.assertEqual(str(version_data), version_str)
            self.assertEqual(type(version_data.range()), Range)
            self.assertEqual(str(version_data.version()), version_base)
            self.assertEqual(str(version_data.range().left()), version_left)
            self.assertEqual(str(version_data.range().right()), version_right)
            self.assertEqual(version_data.range().flags(), range_flags)

if __name__ == "__main__":
    unittest.main()
