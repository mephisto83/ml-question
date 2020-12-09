from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import LatexCharsNode, LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexMathNode, LatexGroupNode
from nodetype import TokenType, MacroTypes
from node import Node
import re
from lexicalbuilderrules import LexicalBuilderRule
from lexicalruleitem import LexicalRuleItem
class MockGroup:
    def __init__(self, list_):
        self.nodelist = list_
class LexicalBuilder:
    def __init__(self):
        self.state = None
        self.eqBuilder = None

    def consume(self, latexNode, lastNode=None, remainingText=None, stack_context=None):
        if isinstance(latexNode, LatexCharsNode) or remainingText != None:
            remaining = None
            if remainingText != None:
                text = remainingText
            else:
                text = str(latexNode.chars)
            # while remaining == None or len(remaining) > 0:
            remaining, currentNode = self.produceNodeFromString(text, stack_context)
            text = "".join(remaining)
            return currentNode, text
        elif isinstance(latexNode, LatexMacroNode):
            currentNode = self.produceNodeFromMacro(latexNode)
            return currentNode, ""
        elif isinstance(latexNode, LatexGroupNode):
            currentNode = self.produceNodeGroupGroup(latexNode)
            return self.parse(currentNode, lastNode), ""
        return currentNode, ""

    def produceNodeFromMacro(self, latexNode):
        if latexNode.macroname == MacroTypes.Times.value:
            return Node(TokenType.T_MULT)
        elif latexNode.macroname == MacroTypes.LParen.value:
            return Node(TokenType.T_LPAR)
        elif latexNode.macroname == MacroTypes.RParen.value:
            return Node(TokenType.T_RPAR)
        elif latexNode.macroname == MacroTypes.Cos.value:
            return Node(TokenType.T_COS)
        elif latexNode.macroname == MacroTypes.Sin.value:
            return Node(TokenType.T_SIN)
        elif latexNode.macroname == MacroTypes.Tan.value:
            return Node(TokenType.T_TAN)
        elif latexNode.macroname == MacroTypes.Integral.value:
            return Node(TokenType.T_INTEGRAL)
        elif latexNode.macroname == MacroTypes.Delta.value:
            return Node(TokenType.T_DELTA)
        raise Exception("unhandled macro : " + latexNode.macroname)

    def produceNodeGroupGroup(self, latexNode):
        groupNode = Node(TokenType.S_GROUP)
        groupNode.setGroupLatex(latexNode)
        return groupNode

    def getTokenType(self, c):
        mappings = {
            '+': TokenType.T_PLUS,
            '-': TokenType.T_MINUS,
            '*': TokenType.T_MULT,
            '/': TokenType.T_DIV,
            '(': TokenType.T_LPAR,
            ')': TokenType.T_RPAR,
            '_': TokenType.S_VERTICAL,
            '^': TokenType.T_POWER,
            ' ': TokenType.S_SPACE,
            '.': TokenType.T_NUM
        }
        letters = list("abcdefghijklmnopqrstuvwxyz")
        token_type = None
        ismatch = re.match(r'\d', c) != None
        if c in mappings:
            token_type = mappings[c]
        elif ismatch:
            token_type = TokenType.T_NUM
        elif c in letters:
            token_type = TokenType.T_VARIABLE
        else:
            raise Exception('Invalid token: {}'.format(c))
        return token_type

    def tokenIsSimple(self, token_type):
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

    def handleSimple(self, currentNode,  inputNode):
        if inputNode == None:
            raise Exception("The simple functions need an input before hand")
        else:
            builder = LexicalBuilderRule.getTypeRule(
                currentNode.getTokenType())
            swapped = False
            if currentNode.isOperator() and inputNode.isOperator():
                sortedNodes = builder.sortOperations([inputNode, currentNode])
                if sortedNodes[0] != inputNode:
                    builder.swapLeftRight(inputNode, currentNode)
                    swapped = True
            if swapped == False:
                builder.consume(currentNode, inputNode)
            # if len(s_list) < 2:
            #     raise Exception(
            #         "Unexpected lack of enough tokens, lexicalbuilder.py")
            # nextchar = s_list[1]
            # nextTokenType = self.getTokenType(nextchar)
            # nextNode = Node(nextTokenType, nextchar)
            # self.parse(nextNode, nextTokenType, currentNode, s_list[1:])
        return currentNode

    def handleFunction(self, currentNode, lastNode = None):
        if lastNode == None:
            raise Exception("Expression expects more info")
        if True:
            builder = LexicalBuilderRule.getTypeRule(
                currentNode.getTokenType())

            builder.consume(currentNode, lastNode)
            return currentNode
        else:
            raise Exception("unabled type, handleFunction")

    def handleExpression(self, currentNode, lastNode=None):
        if lastNode == None:
            raise Exception("Expression expects more info")
        if lastNode.getTokenType() == TokenType.T_CONTEXT or lastNode.getTokenType() == TokenType.T_NUM:
            builder = LexicalBuilderRule.getTypeRule(
                currentNode.getTokenType())
            builder.consume(currentNode, lastNode)
            return currentNode
        else:
            raise Exception("unabled type, handleExpression")

    def handleVariable(self, currentNode, lastNode=None):
        if lastNode != None:
            if lastNode.getTokenType() == TokenType.T_DELTA:
                return self.handleDelta( lastNode, currentNode)
            elif lastNode.getTokenType() == TokenType.S_VERTICAL:
                return self.handleVertical(currentNode, lastNode)

        return self.handleNumber(currentNode, lastNode)
    def handleVertical(self, node, verticalNode):
        if verticalNode.getTokenType() == TokenType.S_VERTICAL:
            builder = LexicalBuilderRule.getTypeRule(verticalNode.getTokenType())
            if builder.isFull(verticalNode):
                return self.parse(node, verticalNode)
            else:
                builder.consume(verticalNode, node)
            return verticalNode
    def handleDelta(self, deltaNode, node):
        if deltaNode.getTokenType() == TokenType.T_DELTA:
            builder = LexicalBuilderRule.getTypeRule(deltaNode.getTokenType())
            if builder.isFull(deltaNode):
                return self.buildContextualMultiply(node, deltaNode)
            else:
                builder.consume(deltaNode, node)
            return deltaNode
        # returns the delta, so that we can add current context to the stack
        elif node.getTokenType() == TokenType.T_DELTA:
            return node

    def handleNumber(self, currentNode, lastNode=None):
        if lastNode == None:
            return currentNode

        lastNodeIsSimple = self.tokenIsSimple(lastNode.getTokenType())

        if lastNodeIsSimple:
            builder = LexicalBuilderRule.getTypeRule(lastNode.getTokenType())
            builder.consume(lastNode, currentNode)
            return lastNode
        elif lastNode.getTokenType() == TokenType.T_CONTEXT or lastNode.getTokenType() == TokenType.T_NUM or lastNode.getTokenType() == TokenType.T_VARIABLE:
            return self.buildContextualMultiply(currentNode, lastNode)
        elif lastNode.isExpression():
            return self.parse(lastNode, currentNode)
        elif lastNode.token_type == TokenType.S_DELIMITER: # Assuming that the delimiter will self-close, 
            return currentNode
        else:
            raise Exception("Unexpected case: handleNumber")

    def buildContextualMultiply(self, contextNode, currentNode):
        _, multiplyNode = self.produceNodeFromString('*')
        multiplyNode = self.parse(multiplyNode, currentNode)
        multiplyNode = self.parse(multiplyNode, contextNode)
        return multiplyNode

    def parse(self, currentNode, lastNode):
        token_type = currentNode.getTokenType()
        issimple = self.tokenIsSimple(token_type)
        if issimple:
            return self.handleSimple(currentNode, lastNode)
        elif token_type == TokenType.T_NUM:
            return self.handleNumber(currentNode, lastNode)
        elif token_type == TokenType.T_VARIABLE:
            return self.handleVariable(currentNode, lastNode)
        elif currentNode.isDelimiter():
            return currentNode
        elif currentNode.isExpression():
            return self.handleExpression(currentNode, lastNode)
        elif token_type == TokenType.T_DELTA:
            return self.handleDelta(currentNode, lastNode)
        elif token_type == TokenType.S_DELIMITER:
            return self.handleSyntaxDelimeter(currentNode, lastNode)
        elif token_type == TokenType.S_GROUP:
            return self.handleGroup(currentNode, lastNode)
        elif currentNode.isFunction():
            return self.handleFunction(currentNode, lastNode)
        elif currentNode.getTokenType() == TokenType.S_VERTICAL:
            return self.handleVertical(lastNode, currentNode)
        elif currentNode.getTokenType() == TokenType.T_INTEGRAL:
            return self.handleIntegral(currentNode, lastNode)
        raise Exception("unhandled parse case  : " + str(token_type))

    def handleIntegral(self, currentNode, lastNode):
        builder = LexicalBuilderRule.getTypeRule(lastNode.getTokenType())
        builder.consume(currentNode, lastNode)
        return currentNode

    def handleGroup(self, currentNode, lastNode):
        if currentNode.hasChildren():
            groupContent = self.buildTree(currentNode.groupLatex)
            return groupContent
        # just return itself, cause it will have to drill down inside.
        return currentNode
    def buildGroup(self, nodeList):
        return self.buildTree(MockGroup(nodeList))
    def buildTree(self, node):
        return self.eqBuilder.buildTree(node)

    def setEqBuilder(self, eqBuilder):
        self.eqBuilder = eqBuilder

    def handleSyntaxDelimeter(self, currentNode, lastNode):
        token_type = lastNode.getTokenType()
        if token_type == TokenType.T_INTEGRAL:
            current_token_type = currentNode.getTokenType()
            possibilities = LexicalBuilderRule.getNextExpectedNodeType(
                current_token_type, token_type, {'contextNode': lastNode})
            currentNode.setContextType(token_type)
            currentNode.setPotentitalTypes(possibilities)
        return currentNode

    def produceNodeFromString(self, s, stack_context = None):
        last_type = None
        currentNode = None
        lastNode = None
        s_list = []
        s_list[:] = s
        for i in range(len(s_list)):
            c = s_list[i]
            token_type = self.getTokenType(c)
            currentNode = Node(token_type, c)

            if token_type == TokenType.T_NUM:
                if last_type == TokenType.T_NUM:
                    lastNode.merge(currentNode)
                    currentNode = lastNode
            elif token_type == TokenType.T_MINUS and lastNode == None and self.getTokenType(s_list[i+1]) == TokenType.T_NUM:
                currentNode.changeTokenType(TokenType.T_NUM)
                token_type = TokenType.T_NUM
            else:
                if last_type == None:
                    return s_list[i+1:], currentNode
                if last_type != token_type:
                    return s_list[i:], lastNode

            lastNode = currentNode
            last_type = token_type

        return [], lastNode

    def lexicalStringAnalysis(self, s):
        mappings = {
            '+': TokenType.T_PLUS,
            '-': TokenType.T_MINUS,
            '*': TokenType.T_MULT,
            '/': TokenType.T_DIV,
            '(': TokenType.T_LPAR,
            ')': TokenType.T_RPAR}

        tokens = []
        for c in s:
            if c in mappings:
                token_type = mappings[c]
                token = Node(token_type, value=c)
            elif re.match(r'\d', c):
                token = Node(TokenType.T_NUM, value=int(c))
            else:
                raise Exception('Invalid token: {}'.format(c))
            tokens.append(token)
        tokens.append(Node(TokenType.T_END))
        return tokens
