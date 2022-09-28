from lexicalruleitem import LexicalRuleItem
from nodetype import TokenType
from operator import itemgetter


def opSort(e):
    tt = e.getTokenType()
    if tt == TokenType.T_CONTEXT:
        return 0
    elif tt == TokenType.T_POWER:
        return 1
    elif tt == TokenType.T_ROOT:
        return 1
    elif tt == TokenType.T_MULT:
        return 2
    elif tt == TokenType.T_DIV:
        return 2
    elif tt == TokenType.T_PLUS:
        return 3
    elif tt == TokenType.T_MINUS:
        return 3
    elif tt == TokenType.T_INTEGRAL:
        return 1
    raise Exception("unhandled opSort")


class LexicalBuilderRule:
    def __init__(self):
        self.expectedItemOrder = []
        self.requiredItems = []

    @staticmethod
    def isNodeFull(node):
        builder = LexicalBuilderRule.getTypeRule(node.getTokenType())
        return builder.isFull(node)

    def isFull(self, node):
        nextMissing = self.getNextMissing(node)
        return nextMissing == None

    def consume(self, node, nextNode):
        nextMissing = self.getNextMissing(node)
        if nextMissing == None:
            raise Exception("Next node missing")
        node.addChild(nextMissing, nextNode)

    def getNextMissing(self, node):
        for i in self.expectedItemOrder:
            if not node.hasChild(i) and i != LexicalRuleItem.K_SELF:
                return i
        return None

    def isNextRuleBeforeSelf(self, node):
        for i in self.expectedItemOrder:
            if not node.hasChild(i) and i != LexicalRuleItem.K_SELF:
                return True
            elif i == LexicalRuleItem.K_SELF:
                return False
        return False

    def isNextRuleAfterSelf(self, node):
        for i in self.expectedItemOrder[::-1]:
            if not node.hasChild(i) and i != LexicalRuleItem.K_SELF:
                return True
            elif i == LexicalRuleItem.K_SELF:
                return False
        return False

    def sortOperations(self, operations):
        array = []
        for i in range(len(operations)):
            array.append((i, operations[i], opSort(operations[i])))
        res = sorted(array, key=itemgetter(2, 0))
        return list(map(lambda x: x[1], res))

    def swapLeftRight(self, left, right):
        leftsRightChild = left.getChild(LexicalRuleItem.K_RIGHT)
        left.addChild(LexicalRuleItem.K_RIGHT, right)
        right.addChild(LexicalRuleItem.K_LEFT, leftsRightChild)

    @staticmethod
    def getTypeRule(typeRule, context=None, params=None):
        if typeRule == TokenType.T_PLUS:
            return LexicalBuilderRule.multiplyRule()
        elif typeRule == TokenType.T_DIV:
            return LexicalBuilderRule.divideRule()
        elif typeRule == TokenType.T_MINUS:
            return LexicalBuilderRule.subtractRule()
        elif typeRule == TokenType.T_MULT:
            return LexicalBuilderRule.multiplyRule()
        elif typeRule == TokenType.T_PLUS:
            return LexicalBuilderRule.additionRule()
        elif typeRule == TokenType.T_POWER:
            return LexicalBuilderRule.powerRule()
        elif typeRule == TokenType.T_COS:
            return LexicalBuilderRule.simpleExpression()
        elif typeRule == TokenType.T_SIN:
            return LexicalBuilderRule.simpleExpression()
        elif typeRule == TokenType.T_TAN:
            return LexicalBuilderRule.simpleExpression()
        elif typeRule == TokenType.T_DELTA:
            return LexicalBuilderRule.deltaExpression()
        elif typeRule == TokenType.T_VARIABLE:
            return LexicalBuilderRule.empty()
        elif typeRule == TokenType.T_NUM:
            return LexicalBuilderRule.empty()
        elif typeRule == TokenType.S_SPACE:
            return LexicalBuilderRule.empty()
        elif typeRule == TokenType.T_INTEGRAL:
            return LexicalBuilderRule.integralExpression()
        elif typeRule == TokenType.S_DELIMITER:
            return LexicalBuilderRule.delimiter(context)
        elif typeRule == TokenType.S_GROUP:
            return LexicalBuilderRule.group()
        elif typeRule == TokenType.S_VERTICAL:
            return LexicalBuilderRule.verticalRule()
        elif typeRule == TokenType.T_CONTEXT:
            return LexicalBuilderRule.contextRule()
        else:
            raise Exception("not handled getTypeRule : " + str(typeRule))

    @staticmethod
    def contextRule():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_MIDDLE]
        result.requiredItems = [
            LexicalRuleItem.K_MIDDLE]
        return result

    @staticmethod
    def verticalRule():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_START, LexicalRuleItem.K_POWER, LexicalRuleItem.K_END]
        result.requiredItems = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_START, LexicalRuleItem.K_POWER, LexicalRuleItem.K_END]
        return result

    @staticmethod
    def delimiter(context):
        if context == None:
            raise Exception("context cant be none for delimiter")
        if TokenType.T_RANGE in context.potentials:
            return LexicalBuilderRule.rangeExpression()

    @staticmethod
    def rangeExpression():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_START, LexicalRuleItem.K_END]
        result.requiredItems = [LexicalRuleItem.K_START, LexicalRuleItem.K_END]
        return result

    @staticmethod
    def group():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [LexicalRuleItem.K_PARAM1]
        result.requiredItems = [LexicalRuleItem.K_PARAM1]
        return result

    @staticmethod
    def getNextExpectedNodeType(typeRule, context=None, params=None):
        if typeRule == TokenType.S_DELIMITER:
            if context == TokenType.T_INTEGRAL:
                return LexicalBuilderRule.IntegralRules(typeRule, context, params)
        raise Exception("unexpected typeRule " + str(typeRule))

    @staticmethod
    def IntegralRules(typeRule, context, params):
        if params == None:
            raise Exception("integral rules need contextual information")
        contextNode = params['contextNode']
        nextRule = LexicalBuilderRule.getNodesNextRule(contextNode)
        if nextRule == LexicalRuleItem.K_RANGE:
            return [TokenType.T_RANGE]  # RETURNS A TUPLE OF POSSIBILITIES
        elif nextRule == LexicalRuleItem.K_MIDDLE:
            res = []
            for i in TokenType:
                if i != TokenType.T_DELTA:
                    res.append(i)
            return res

    @staticmethod
    def getNodesNextRule(node):
        builder = LexicalBuilderRule.getTypeRule(node.getTokenType())
        return builder.getNextMissing(node)

    @staticmethod
    def multiplyRule():
        return LexicalBuilderRule.simpleRule()

    @staticmethod
    def divideRule():
        return LexicalBuilderRule.simpleRule()

    @staticmethod
    def additionRule():
        return LexicalBuilderRule.simpleRule()

    @staticmethod
    def powerRule():
        return LexicalBuilderRule.simpleRule()

    @staticmethod
    def subtractRule():
        return LexicalBuilderRule.simpleRule()

    @staticmethod
    def simpleRule():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_LEFT, LexicalRuleItem.K_SELF, LexicalRuleItem.K_RIGHT]
        result.requiredItems = [LexicalRuleItem.K_LEFT,
                                LexicalRuleItem.K_SELF, LexicalRuleItem.K_RIGHT]
        return result

    @staticmethod
    def simpleExpression():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_PARAM1]
        result.requiredItems = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_PARAM1]
        return result

    @staticmethod
    def empty():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [LexicalRuleItem.K_SELF]
        result.requiredItems = [LexicalRuleItem.K_SELF]
        return result

    @staticmethod
    def deltaExpression():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_WITH_RESPECT]
        result.requiredItems = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_WITH_RESPECT]
        return result

    @staticmethod
    def integralExpression():
        result = LexicalBuilderRule()
        result.expectedItemOrder = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_RANGE,  LexicalRuleItem.K_MIDDLE, LexicalRuleItem.K_DELTA]
        result.requiredItems = [
            LexicalRuleItem.K_SELF, LexicalRuleItem.K_RANGE, LexicalRuleItem.K_MIDDLE, LexicalRuleItem.K_DELTA]
        return result
