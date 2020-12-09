import enum

class LexicalRuleItem(enum.Enum):
    K_LEFT = 0
    K_RIGHT = 1
    K_SELF = 2
    K_MIDDLE = 3
    K_PARAM1 = 4
    K_WITH_RESPECT = 5
    K_DELTA = 6
    K_RANGE = 7
    K_END = 8
    K_START = 9
    K_POWER = 10