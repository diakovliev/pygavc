import unittest

from gavc.versions_comparator import VersionsComparator
from gavc.version import VersionData

class VersionsComparatorTests(unittest.TestCase):

    def test_versions_comparator(self):
        version_data = VersionData.parse("*.*.*")
        comparator = VersionsComparator(version_data.version())

        # Syntax: compare(obj1, obj2)
        # compare() will return negative (-1) if obj1<obj2, zero (0) if obj1=obj2, positive (1) if obj1>obj2.

        # Basic numeric cases
        self.assertTrue(0 == comparator.compare("0.0.0", "0.0.0"))
        self.assertTrue(0 == comparator.compare("0.1.0", "0.1.0"))
        self.assertTrue(0 == comparator.compare("1.0.0", "1.0.0"))
        self.assertTrue(0 == comparator.compare("1.1.0", "1.1.0"))
        self.assertTrue(0 == comparator.compare("1.1.1", "1.1.1"))

        self.assertTrue(0  > comparator.compare("0.0.0", "0.0.1"))
        self.assertTrue(0  > comparator.compare("1.0.0", "1.0.1"))
        self.assertTrue(0  > comparator.compare("1.1.0", "1.1.1"))

        self.assertTrue(0  < comparator.compare("0.0.1", "0.0.0"))
        self.assertTrue(0  < comparator.compare("1.0.1", "1.0.0"))
        self.assertTrue(0  < comparator.compare("1.1.1", "1.1.0"))

        # Basic lexicographic cases
        self.assertTrue(0 == comparator.compare("a.b.c", "a.b.c"))
        self.assertTrue(0 == comparator.compare("0.a.0", "0.a.0"))
        self.assertTrue(0 == comparator.compare("b.0.0", "b.0.0"))
        self.assertTrue(0 == comparator.compare("a.b.0", "a.b.0"))
        self.assertTrue(0 == comparator.compare("c.a.b", "c.a.b"))

        self.assertTrue(0  > comparator.compare("0.0.0", "0.0.a"))
        self.assertTrue(0  > comparator.compare("a.0.0", "a.0.b"))
        self.assertTrue(0  > comparator.compare("a.b.0", "a.b.c"))

        self.assertTrue(0  < comparator.compare("0.0.a", "0.0.0"))
        self.assertTrue(0  < comparator.compare("a.0.b", "a.0.0"))
        self.assertTrue(0  < comparator.compare("a.b.c", "a.b.0"))

        # Mixed cases
        self.assertTrue(0  > comparator.compare("0.0.a", "0.0.a1"))
        self.assertTrue(0  < comparator.compare("0.0.a", "0.0.1a"))
        self.assertTrue(0  > comparator.compare("0.0.a18", "0.0.a8"))
        self.assertTrue(0  < comparator.compare("0.0.aaaa", "0.0.aa1aaaaaa"))

if __name__ == "__main__":
    unittest.main()
