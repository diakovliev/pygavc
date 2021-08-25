import re

from lark import Lark

grammar = """
    start: bra? version ( "," version ket? )?
    inc_bra: "["
    inc_ket: "]"
    exc_bra: "("
    exc_ket: ")"
    bra: inc_bra | exc_bra
    ket: inc_ket | exc_ket
    op_all: "*"
    op_oldest: "-"
    op_latest: "+"
    op_const: /[0-9a-zA-Z\.\_]+/
    ops: op_const | op_oldest | op_latest | op_all
    version: ops+
"""


class Op:
    OP_CONST   = ""
    OP_ALL     = "*"
    OP_OLDEST  = "-"
    OP_LATEST  = "+"

    def __init__(self, op, data):
        self.__op   = op
        self.__data = data

    def op(self):
        return self.__op

    def data(self):
        return self.__data


class Range:
    INCLUDE_ALL     = 0x00
    INCLUDE_LEFT    = 0x01
    INCLUDE_RIGHT   = 0x02

    def __init__(self, left, right, flags):
        self.__left     = left
        self.__right    = right
        self.__flags    = flags

    def left(self):
        return self.__left

    def right(self):
        return self.__right

    def data(self):
        return self.__data


if __name__ == "__main__":
    tree = Lark(grammar, parser='lalr').parse("[12.1.-,12.5.+)")
    print(tree.pretty())
