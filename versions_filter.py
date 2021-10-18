from functools import cmp_to_key

from version import Op
from version import Range
from version import Version
from version import VersionData
from versions_matcher import VersionsMatcher
from versions_comparator import VersionsComparator
from sparts_table_comparator import SPartsTableElement
from sparts_table_comparator import SpartsTableComparator

class VersionsFilter:

    def __init__(self, version_data):
        self.__version = version_data.version()
        self.__range = version_data.range()
        self.__matcher = VersionsMatcher(self.__version)
        self.__comparator = VersionsComparator(self.__version)

    def __filtered(self, versions):
        result = versions.copy()

        # 1. Filter out all non matched versions.
        result = list(filter(lambda version: self.__matcher.match(version), result))

        if len(result) == 0:
            return result

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

    def __get_border_version(self, version_template, versions):
        exists = True
        result = None

        if version_template.is_const():
            exists = str(version_template) in versions
            result = str(version_template)
        elif version_template.is_single_version():
            border_filter = VersionsFilter(VersionData(version_template))
            filtered = border_filter.filtered(versions)
            if len(filtered):
                result = filtered[0]

        return (result, exists)

    def __filtered_range(self, versions):
        result = list()

        if (not self.__version) or (not self.__range):
            return result

        filtered_versions = list(filter(lambda version: self.__matcher.match(version), versions))

        if len(filtered_versions) == 0:
            return result

        left_version = self.__get_border_version(self.__range.left(), filtered_versions)
        if not left_version[0]:
            return result

        right_version = self.__get_border_version(self.__range.right(), filtered_versions)
        if not right_version[0]:
            return result

        if self.__comparator.compare(left_version[0], right_version[0]) >= 0:
            return result;

        if (self.__range.flags() & Range.INCLUDE_LEFT) and left_version[1]:
            result.append(left_version[0])

        for fversion in filtered_versions:
            if (self.__comparator.compare(left_version[0], fversion) < 0) and (self.__comparator.compare(right_version[0], fversion) > 0):
                result.append(fversion)

        if (self.__range.flags() & Range.INCLUDE_RIGHT) and right_version[1]:
            result.append(right_version[0])

        result.sort(key=cmp_to_key(self.__comparator.compare))

        return result

    def filtered(self, versions):
        if self.__range:
            return self.__filtered_range(versions)
        return self.__filtered(versions)

    def filtered_out(self, versions):
        filtered = self.filtered(versions)
        filtered_out = [version for version in versions if version not in filtered]
        return filtered_out

def __filter_versions(base_version_str, versions):
    base_version = VersionData.parse(base_version_str)
    vfilter = VersionsFilter(base_version)
    filtered = vfilter.filtered(versions)
    print("Base version: '" + str(base_version) +"'")
    print(filtered)

if __name__ == "__main__":
    versions = ["16.6.6", "16.6.2", "16.9.18", "16.1.3", "16.9.8", "1.6.6", "16.1.8", "16.6.983", "16.6.12"]
    print(versions)
    __filter_versions("16.-.+",  versions)
    __filter_versions("16.*.+",  versions)
    __filter_versions("16.6.*",  versions)
    __filter_versions("16.*",  versions)

    print("\n")

    __filter_versions("16.6.*[16.6.2,16.6.12]",  versions)
    __filter_versions("16.6.*(16.6.2,16.6.12]",  versions)
    __filter_versions("16.6.*[16.6.2,16.6.12)",  versions)
    __filter_versions("16.6.*(16.6.2,16.6.12)",  versions)

