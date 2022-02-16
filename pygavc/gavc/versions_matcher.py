import re

from .version import Op
from .version import Version
from .version import VersionData

class VersionsMatcher:

    def __init__(self, version):
        self.__regex = self.__create_regex(version)

    def __create_regex(self, version):
        regex = ""
        delimiter = ""
        for op in version.ops():
            regex += delimiter
            if op.op() == Op.OP_CONST:
                regex += re.escape(op.data())
            else:
                regex += "(.+)"
            delimiter = re.escape(Op.OP_DEL)
        return re.compile(regex)

    def match(self, version):
        match = self.__regex.fullmatch(str(version))
        return False if match == None else True

    def significant_parts(self, version):
        match = self.__regex.fullmatch(str(version))
        return match.groups() if match else None


if __name__ == "__main__":
    version = (VersionData.parse("16.6.*").version())
    matcher = VersionsMatcher(version)
    print(matcher.significant_parts("16.6.8.78"))
    version = (VersionData.parse("+.-.*").version())
    matcher = VersionsMatcher(version)
    print(matcher.significant_parts("16.7.2"))
