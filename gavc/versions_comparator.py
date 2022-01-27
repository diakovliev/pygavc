from .versions_matcher import VersionsMatcher

class VersionsComparator:

    def __init__(self, version):
        self.__matcher = VersionsMatcher(version)

    def compare_part(self, left, right):
        if left == right:
            return 0

        if left.isnumeric() and right.isnumeric():
            return -1 if int(left) < int(right) else 1

        return -1 if left < right else 1

    def compare(self, left, right):
        result = 0

        if left == right:
            return result

        left_parts = self.__matcher.significant_parts(left)
        right_parts = self.__matcher.significant_parts(right)

        if len(left_parts) != len(right_parts):
            return NotImplemented

        for left_part, right_part in zip(left_parts, right_parts):
            result = self.compare_part(left_part, right_part)
            if result != 0:
                break

        return result
