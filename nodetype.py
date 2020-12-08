import enum

class TokenType(enum.Enum):
    T_NUM = 0
    T_PLUS = 1
    T_MINUS = 2
    T_MULT = 3
    T_DIV = 4
    T_LPAR = 5
    T_RPAR = 6
    T_END = 7
    T_CONTEXT = 8 # ( x + 3 )
    T_COS = 9
    T_SIN = 10
    T_TAN = 11
    T_INTEGRAL = 12
    T_RANGE = 13
    S_DELIMITER = 14
    S_GROUP = 15
    T_POWER = 16
    T_ROOT = 17
    T_VARIABLE = 18
    T_DELTA = 19

class MacroTypes(enum.Enum):
    Times = "times"
    LParen = "lparen"
    RParen = "rparen"
    Cos = "cos"
    Sin = "sin"
    Tan = "tan"
    Integral = "int"
    Delta = "delta"