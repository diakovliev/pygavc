import unittest

from versions_matcher import VersionsMatcher
from version import VersionData

class VersionsMatcherTests(unittest.TestCase):

    def setUp(self):
        self.significant_parts_test_data = list()
        self.significant_parts_test_data.append(("+.-.*", "0.0.1", ("0", "0", "1")))
        self.significant_parts_test_data.append(("*.+.-", "0.1.0", ("0", "1", "0")))
        self.significant_parts_test_data.append(("-.+.*", "1.0.0", ("1", "0", "0")))
        self.significant_parts_test_data.append(("*.-.*", "1.0.1", ("1", "0", "1")))
        self.significant_parts_test_data.append(("+.*.-", "1.1.0", ("1", "1", "0")))
        self.significant_parts_test_data.append(("*.+.*", "1.1.1", ("1", "1", "1")))
        self.significant_parts_test_data.append(("-.*.+", "111.11.0", ("111", "11", "0")))
        self.significant_parts_test_data.append(("+.-", "111.11", ("111", "11")))
        self.significant_parts_test_data.append(("-", "111", ("111",)))

    def test_significant_parts_simple(self):
        version_data = VersionData.parse("12.6.*.123.+.*")
        matcher = VersionsMatcher(version_data.version())
        significant_parts = matcher.significant_parts("12.6.ods.123.4453.987")

        self.assertEqual(len(significant_parts), 3)
        self.assertEqual(significant_parts[0], "ods")
        self.assertEqual(significant_parts[1], "4453")
        self.assertEqual(significant_parts[2], "987")

    def test_significant_parts_list(self):
        for item in self.significant_parts_test_data:
            base_version_str, match_version_str, match_significant_parts = item

            version_data = VersionData.parse(base_version_str)
            matcher = VersionsMatcher(version_data.version())
            significant_parts = matcher.significant_parts(match_version_str)

            self.assertEqual(len(match_significant_parts), len(significant_parts))
            for i in range(len(match_significant_parts)):
                self.assertEqual(match_significant_parts[i], significant_parts[i])

if __name__ == "__main__":
    unittest.main()
