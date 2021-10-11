from functools import cmp_to_key

from version import Op
from version import Version
from version import VersionData
from versions_matcher import VersionsMatcher
from versions_comparator import VersionsComparator
from sparts_table_comparator import SPartsTableElement
from sparts_table_comparator import SpartsTableComparator

class VersionsFilter:

    def __init__(self, version):
        self.__version = version
        self.__matcher = VersionsMatcher(version)
        self.__comparator = VersionsComparator(version)

    def filtered(self, versions):
        result = versions.copy()

        # 1. Filter out all non matched versions.
        result = list(filter(lambda version: self.__matcher.match(version), result))

        # 2. Process significant parts. Build table <version, [significant parts]>
        sparts_table = list()
        for version in result:
            sparts_table.append(SPartsTableElement(version, self.__matcher.significant_parts(version)))

        # 3. For each version op filter out elements from sparts_table according to op
        part_index = 0
        for op in self.__version.ops():
            if (op.op() == Op.OP_OLDEST) or (op.op() == Op.OP_LATEST):
                sparts_comparator = SpartsTableComparator(self.__comparator, op, part_index)
                sparts_table.sort(key=cmp_to_key(sparts_comparator.compare))
                element_to_keep = max(sparts_table, key=cmp_to_key(sparts_comparator.compare))
                sparts_table = sparts_table[sparts_table.index(element_to_keep):]

            if op.op() != Op.OP_CONST:
                part_index += 1

        # 4. Copy results into result
        result = [element.version() for element in sparts_table]

        # 5. Sort results
        result.sort(key=cmp_to_key(self.__comparator.compare))

        return result

    def filtered_out(self, versions):
        filtered = self.filtered(versions)
        filtered_out = [version for version in versions if version not in filtered]
        return filtered_out

def __filter_versions(base_version_str, versions):
    base_version = (VersionData.parse(base_version_str).version())
    vfilter = VersionsFilter(base_version)
    filtered = vfilter.filtered(versions)
    print("Base version: '" + str(base_version) +"'")
    print(filtered)

if __name__ == "__main__":
    versions = ["16.6.6", "16.6.2", "16.9.18", "16.1.3", "16.9.8", "1.6.6", "16.1.8", "16.6.983"]
    print(versions)
    __filter_versions("16.-.+",  versions)
    __filter_versions("16.*.+",  versions)
    __filter_versions("16.6.*",  versions)
    __filter_versions("16.*",  versions)
