import unittest

from versions_filter import VersionsFilter
from versions_filter import VersionsRangeFilter
from version import VersionData

class VersionsFilterTests(unittest.TestCase):

    def setUp(self):
        self.versions_test_data_1 = list()
        self.versions_test_data_1.append("1234")
        self.versions_test_data_1.append("1223")
        self.versions_test_data_1.append("12")
        self.versions_test_data_1.append("16.6.123")
        self.versions_test_data_1.append("16.6.536")

        self.versions_test_data_2 = list()
        self.versions_test_data_2.append("16.6.6")
        self.versions_test_data_2.append("16.6.2")
        self.versions_test_data_2.append("16.9.18")
        self.versions_test_data_2.append("16.1.3")
        self.versions_test_data_2.append("16.9.8")
        self.versions_test_data_2.append("16.1.8")
        self.versions_test_data_2.append("16.6.983")

    def test_basic_filtering(self):
        version_data = VersionData.parse("16.6.*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_1)

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.536")

        filtered_out = vfilter.filtered_out(self.versions_test_data_1)

        self.assertEqual(len(filtered_out), 3)
        self.assertEqual(filtered_out[0], "1234")
        self.assertEqual(filtered_out[1], "1223")
        self.assertEqual(filtered_out[2], "12")

    def test_basic_filter_all(self):
        version_data = VersionData.parse("*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_1)

        self.assertEqual(len(filtered), len(self.versions_test_data_1))
        self.assertEqual(filtered[0], "12")
        self.assertEqual(filtered[1], "1223")
        self.assertEqual(filtered[2], "1234")
        self.assertEqual(filtered[3], "16.6.123")
        self.assertEqual(filtered[4], "16.6.536")

        filtered_out = vfilter.filtered_out(self.versions_test_data_1)

        self.assertEqual(len(filtered_out), 0)

    def test_filter_out_all(self):
        version_data = VersionData.parse("12.6.*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_1)

        self.assertEqual(len(filtered), 0)

        filtered_out = vfilter.filtered_out(self.versions_test_data_1)

        self.assertEqual(len(filtered_out), len(self.versions_test_data_1))
        self.assertEqual(filtered_out[0], "1234")
        self.assertEqual(filtered_out[1], "1223")
        self.assertEqual(filtered_out[2], "12")
        self.assertEqual(filtered_out[3], "16.6.123")
        self.assertEqual(filtered_out[4], "16.6.536")

    def test_filter_all_plus(self):
        version_data = VersionData.parse("16.*.+")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_1)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "16.6.536")

    def test_filter_all_plus(self):
        version_data = VersionData.parse("16.*.-")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_1)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "16.6.123")

    def test_filter_minus_plus(self):
        version_data = VersionData.parse("16.-.+")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "16.1.8")

    def test_filter_minus_plus(self):
        version_data = VersionData.parse("16.-.-")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "16.1.3")

    def test_filter_plus_all(self):
        version_data = VersionData.parse("16.+.*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0], "16.9.8")
        self.assertEqual(filtered[1], "16.9.18")

    def test_filter_plus_all(self):
        version_data = VersionData.parse("16.-.*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0], "16.1.3")
        self.assertEqual(filtered[1], "16.1.8")

    def test_filter_all_plus_extended(self):
        version_data = VersionData.parse("16.*.+")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "16.6.983")

    def test_filter_const_const_all(self):
        version_data = VersionData.parse("16.6.*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 3)
        self.assertEqual(filtered[0], "16.6.2")
        self.assertEqual(filtered[1], "16.6.6")
        self.assertEqual(filtered[2], "16.6.983")

    def test_filter_const_all(self):
        version_data = VersionData.parse("16.*")
        vfilter = VersionsFilter(version_data.version())

        filtered = vfilter.filtered(self.versions_test_data_2)

        self.assertEqual(len(filtered), 7)
        self.assertEqual(filtered[0], "16.1.3")
        self.assertEqual(filtered[1], "16.1.8")
        self.assertEqual(filtered[2], "16.6.2")
        self.assertEqual(filtered[3], "16.6.6")
        self.assertEqual(filtered[4], "16.6.983")
        self.assertEqual(filtered[5], "16.9.18")
        self.assertEqual(filtered[6], "16.9.8")

class VersionsRangeFilterTests(unittest.TestCase):

    def setUp(self):
        self.versions_test_data = list()
        self.versions_test_data.append("16.3.123")
        self.versions_test_data.append("16.3.532")
        self.versions_test_data.append("16.6.123")
        self.versions_test_data.append("16.6.124")
        self.versions_test_data.append("16.6.125")
        self.versions_test_data.append("16.6.533")
        self.versions_test_data.append("16.8.123")
        self.versions_test_data.append("16.8.536")

    def test_non_existing_borders(self):
        version_data = VersionData.parse("16.6.*[16.6.122,16.6.534]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 4)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.124")
        self.assertEqual(filtered[2], "16.6.125")
        self.assertEqual(filtered[3], "16.6.533")

    def test_wrong_borders_order(self):
        version_data = VersionData.parse("16.6.*[16.6.533,16.6.123]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 0)

    def test_include_borders(self):
        version_data = VersionData.parse("16.6.*[16.6.-,16.6.+]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 4)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.124")
        self.assertEqual(filtered[2], "16.6.125")
        self.assertEqual(filtered[3], "16.6.533")

        version_data = VersionData.parse("16.6.*[16.6.123,16.6.533]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 4)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.124")
        self.assertEqual(filtered[2], "16.6.125")
        self.assertEqual(filtered[3], "16.6.533")

        version_data = VersionData.parse("16.6.*[16.6.122,16.6.534]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 4)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.124")
        self.assertEqual(filtered[2], "16.6.125")
        self.assertEqual(filtered[3], "16.6.533")

    def test_exclude_left_border(self):
        version_data = VersionData.parse("16.6.*(16.6.-,16.6.+]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 3)
        self.assertEqual(filtered[0], "16.6.124")
        self.assertEqual(filtered[1], "16.6.125")
        self.assertEqual(filtered[2], "16.6.533")

        version_data = VersionData.parse("16.6.*(16.6.123,16.6.533]")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 3)
        self.assertEqual(filtered[0], "16.6.124")
        self.assertEqual(filtered[1], "16.6.125")
        self.assertEqual(filtered[2], "16.6.533")

    def test_exclude_right_border(self):
        version_data = VersionData.parse("16.6.*[16.6.-,16.6.+)")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 3)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.124")
        self.assertEqual(filtered[2], "16.6.125")

        version_data = VersionData.parse("16.6.*[16.6.123,16.6.533)")
        vrfilter = VersionsRangeFilter(version_data)

        filtered = vrfilter.filtered(self.versions_test_data)

        self.assertEqual(len(filtered), 3)
        self.assertEqual(filtered[0], "16.6.123")
        self.assertEqual(filtered[1], "16.6.124")
        self.assertEqual(filtered[2], "16.6.125")


if __name__ == "__main__":
    unittest.main()
