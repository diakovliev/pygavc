import re
import lark

from lark import Lark
from lark import Transformer


################################################################################
class Op:
    OP_CONST   = ""
    OP_ALL     = "*"
    OP_OLDEST  = "-"
    OP_LATEST  = "+"
    OP_DEL     = "."

    def __init__(self, op, data):
        self.__op   = op
        self.__data = data

    def op(self):
        return self.__op

    def data(self):
        return self.__data



################################################################################
class Version:

    def __init__(self, ops = []):
        self.__ops = ops

    def __str__(self):
        ret = ""
        delimiter = ""
        for op in self.__ops:
            ret += delimiter
            ret += op.data()
            delimiter = Op.OP_DEL
        return ret

    def ops(self):
        return self.__ops

    def is_const(self):
        for op in self.__ops:
            if op.op() != Op.OP_CONST:
                return False
        return True

    def is_single_version(self):
        if not len(self.__ops):
            return False
        return self.__ops[-1].op() != Op.OP_ALL



################################################################################
class Range:
    EXCLUDE_ALL     = 0x00
    INCLUDE_LEFT    = 0x01
    INCLUDE_RIGHT   = 0x02

    def __init__(self, left, right, flags):
        self.__left     = left
        self.__right    = right
        self.__flags    = flags

    def __str__(self):
        ret = "[" if (self.__flags & Range.INCLUDE_LEFT) else "("
        ret += str(self.__left) + "," + str(self.__right)
        ret += "]" if (self.__flags & Range.INCLUDE_RIGHT) else ")"
        return ret

    def left(self):
        return self.__left

    def right(self):
        return self.__right

    def flags(self):
        return self.__flags



################################################################################
class VersionData:
    GRAMMAR = """
        start: version version_range?
        include_left: "["
        include_right: "]"
        exclude_left: "("
        exclude_right: ")"
        left_bracket: include_left | exclude_left
        right_bracket: include_right | exclude_right
        op_all: "*"
        op_oldest: "-"
        op_latest: "+"
        op_const: /[0-9a-zA-Z\_]+/
        op_del: "."
        ops: op_const | op_oldest | op_latest | op_all
        version: ops (op_del ops)*
        version_range: left_bracket version "," version right_bracket
    """

    def __init__(self, version = None, versions_range = None):
        self.__version = version
        self.__range = versions_range

    def __str__(self):
        ret = str(self.__version)
        if self.__range:
            ret += str(self.__range)
        return ret

    def version(self):
        return self.__version

    def range(self):
        return self.__range

    def is_const(self):
        if self.__version is None:
            return False
        return self.__version.is_const()

    def is_single_version(self):
        if self.__version is None:
            return False
        return self.__version.is_single_version()

    @staticmethod
    def parse(input_string):
        try:
            tree = Lark(VersionData.GRAMMAR, parser='lalr').parse(input_string)
            return _VersionDataTransformer().transform(tree)
        except lark.exceptions.UnexpectedToken:
            return None



################################################################################
class _VersionDataTransformer(Transformer):
    def start(self, items):
        if len(items) >= 2:
            return VersionData(items[0], items[1])
        return VersionData(items[0])

    def version(self, items):
        ops = list()
        for item in items:
            if type(item) == Op:
                ops.append(item)
        return Version(ops)

    def ops(self, op):
        return op[0]

    def op_const(self, s):
        return Op(Op.OP_CONST, s[0])

    op_all = lambda self,       _: Op(Op.OP_ALL, "*")
    op_oldest = lambda self,    _: Op(Op.OP_OLDEST, "-")
    op_latest = lambda self,    _: Op(Op.OP_LATEST, "+")
    # op_del = lambda self,       _: Op(Op.OP_DEL, ".")
    op_del = lambda self,       _: Op.OP_DEL

    def version_range(self, items):
        left_bracket, left_version, right_version, right_bracket = items
        return Range(left_version, right_version, left_bracket | right_bracket)

    def left_bracket(self, bracket_flag):
        return bracket_flag[0]

    def right_bracket(self, bracket_flag):
        return bracket_flag[0]

    include_left = lambda self, _: Range.INCLUDE_LEFT
    exclude_left = lambda self, _: Range.EXCLUDE_ALL
    include_right = lambda self, _: Range.INCLUDE_RIGHT
    exclude_right = lambda self, _: Range.EXCLUDE_ALL


################################################################################
if __name__ == "__main__":
    print(VersionData.parse(""))
    print(VersionData.parse("16.6.++"))
    print(VersionData.parse("12.*.*(12.1.-,12.5.+]"))
    print(VersionData.parse("16.6.*[16.6.123,16.6.533)"))
