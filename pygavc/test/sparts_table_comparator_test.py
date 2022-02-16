import unittest

from ..gavc.versions_comparator import VersionsComparator
from ..gavc.sparts_table_comparator import SPartsTableElement
from ..gavc.sparts_table_comparator import SpartsTableComparator
from ..gavc.version import VersionData
from ..gavc.version import Op

class SPartsTableComparatorTests(unittest.TestCase):

    def test_sparts_table_comparator(self):
        version_data = VersionData.parse("*.*.*")
        comparator = VersionsComparator(version_data.version())

        op_oldest = Op(Op.OP_OLDEST, "-")
        op_latest = Op(Op.OP_LATEST, "+")

        left = SPartsTableElement("16.6.8", ("16", "6", "8"))
        right = SPartsTableElement("16.8.1", ("16", "8", "1"))

        sparts_comparator_oldest = SpartsTableComparator(comparator, op_oldest, 0)
        sparts_comparator_latest = SpartsTableComparator(comparator, op_latest, 0)

        self.assertTrue(0 == sparts_comparator_oldest.compare(left, right))
        self.assertTrue(0 == sparts_comparator_latest.compare(left, right))

        sparts_comparator_oldest = SpartsTableComparator(comparator, op_oldest, 1)
        sparts_comparator_latest = SpartsTableComparator(comparator, op_latest, 1)

        self.assertTrue(0 < sparts_comparator_oldest.compare(left, right))
        self.assertTrue(0 > sparts_comparator_latest.compare(left, right))

        sparts_comparator_oldest = SpartsTableComparator(comparator, op_oldest, 2)
        sparts_comparator_latest = SpartsTableComparator(comparator, op_latest, 2)

        self.assertTrue(0 > sparts_comparator_oldest.compare(left, right))
        self.assertTrue(0 < sparts_comparator_latest.compare(left, right))

if __name__ == "__main__":
    unittest.main()
