from version import Op
from versions_comparator import VersionsComparator

class SPartsTableElement:

    def __init__(self, version, significant_parts):
        self.__version = version
        self.__significant_parts = significant_parts

    def version(self):
        return self.__version

    def significant_parts(self):
        return self.__significant_parts

class SpartsTableComparator:

    def __init__(self, comparator, op, part_index):
        self.__comparator = comparator
        self.__op = op
        self.__part_index = part_index

    def compare(self, left, right):
        left_part = left.significant_parts()[self.__part_index]
        right_part = right.significant_parts()[self.__part_index]

        if self.__op.op() == Op.OP_LATEST:
            return self.__comparator.compare_part(left_part, right_part)
        if self.__op.op() == Op.OP_OLDEST:
            return self.__comparator.compare_part(right_part, left_part)
        return NotImplemented
