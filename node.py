from nodetype import TokenType
import uuid
from lexicalbuilderrules import LexicalBuilderRule


class Node:
    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.groupLatex = None
        self.value = value
        self.contextType = None
        self.parent = None
        self.potentials = None
        self.satisfyingNode = None
        self.id = uuid.uuid4()
        self.children = {}

    def getValue(self):
        return self.value

    def getTreeIds(self):
        ids = [self.id]
        for i, k in enumerate(self.children):
            ids = ids + self.children[k].getTreeIds()
        return ids

    def findNode(self, id):
        if self.getId() == id:
            return self
        for i, k in enumerate(self.children):
            found = self.children[k].findNode(id)
            if found != None:
                return found
        return None

    def buildGraph(self, graph):
        graph[self.id] = []
        if self.parent != None:
            graph[self.id].append(self.parent.getId())
        for i, k in enumerate(self.children):
            graph[self.id].append(self.children[k].getId())
            self.children[k].buildGraph(graph)

    def getId(self):
        return self.id

    def hasChild(self, name):
        if name in self.children:
            return True
        return False

    def getChild(self, name):
        if self.hasChild(name):
            return self.children[name]
        return None

    def isSelfClosing(self):
        if self.token_type == TokenType.T_DELTA:
            return True
        if self.token_type == TokenType.T_INTEGRAL:
            return True
        if self.token_type == TokenType.T_VARIABLE:
            return True
        if self.token_type == TokenType.T_NUM:
            return True
        if self.token_type == TokenType.S_DELIMITER:
            return self.contextType == TokenType.T_INTEGRAL
        if self.token_type == TokenType.S_VERTICAL:
            return True
        if self.token_type == TokenType.T_POWER:
            return True
        if self.token_type == TokenType.T_CONTEXT:
            return True
        return False

    def hasChildren(self):
        if self.token_type == TokenType.S_GROUP:
            return True

    def getPotentials(self):
        return self.potentials

    def setPotentitalTypes(self, potentials):
        self.potentials = potentials

    def setContextType(self, contextType):
        self.contextType = contextType

    def closesWith(self, val):
        if self.token_type == TokenType.S_DELIMITER:
            if self.contextType == TokenType.T_INTEGRAL:
                return val == ' '
        return False

    @staticmethod
    def closeSelf():
        return Node(None, "$close$")

    def isClosingSelf(self):
        return self.value == '$close$'

    def isClosing(self):
        if self.isSelfClosing():
            builder = LexicalBuilderRule.getTypeRule(self.token_type, self)
            return builder.isFull(self)
        return False

    def isLexicalContextChanging(self):
        return self.token_type == TokenType.T_INTEGRAL

    def lookAhead(self):
        builder = LexicalBuilderRule.getTypeRule(self.token_type, self)
        return builder.isNextRuleBeforeSelf(self)

    def lookBehind(self):
        builder = LexicalBuilderRule.getTypeRule(self.token_type, self)
        return builder.isNextRuleAfterSelf(self)

    def isDelimiter(self):
        return self.token_type == TokenType.T_LPAR or self.token_type == TokenType.T_RPAR

    def isOpeningDelimeter(self):
        return self.token_type == TokenType.T_LPAR

    def peekStack(self, stack):
        if len(stack) > 0:
            return stack[-1]['ln']
        return None

    def isClosingDelimiter(self):
        return self.token_type == TokenType.T_RPAR

    def isOperator(self):
        return self.tokenIsSimple() or self.isExpression() or self.isFunction()

    def isFunction(self):
        token_type = self.token_type
        if token_type == TokenType.T_INTEGRAL:
            return True
        return False

    def isExpression(self):
        token_type = self.token_type
        if token_type == TokenType.T_COS:
            return True
        if token_type == TokenType.T_SIN:
            return True
        if token_type == TokenType.T_TAN:
            return True
        return False

    def isContextual(self):
        token_type = self.token_type
        if token_type == TokenType.T_POWER:
            return True
        return False

    def tokenIsSimple(self):
        token_type = self.token_type
        if token_type == TokenType.T_MINUS:
            return True
        if token_type == TokenType.T_DIV:
            return True
        if token_type == TokenType.T_MINUS:
            return True
        if token_type == TokenType.T_MULT:
            return True
        if token_type == TokenType.T_PLUS:
            return True
        if token_type == TokenType.T_POWER:
            return True
        return False

    def setSatisfyingNode(self, _part):
        self.satisfyingNode = _part

    def changeTokenType(self, type_):
        self.token_type = type_

    def getTokenType(self):
        return self.token_type

    def isGreedy(self):
        return self.token_type == TokenType.S_VERTICAL

    def changeChildKey(self, name, to):
        if self.hasChild(name):
            self.addChild(to, self.getChild(name))
            del self.children[name]

    def addChild(self, name, childNode):
        self.children[name] = childNode
        childNode.setParent(self)

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent

    def setGroupLatex(self, group):
        self.groupLatex = group

    def merge(self, node):
        if self.token_type != node.token_type:
            raise Exception('Cant merge nodes with different type')
        self.value = self.value + node.value
