from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexMathNode
from lexicalbuilder import LexicalBuilder
from lexicalbuilderrules import LexicalBuilderRule
from nodetype import TokenType
from node import Node
from lexicalruleitem import LexicalRuleItem


class EquationData:
    def __init__(self, equation):
        self.equation = EquationData.massageEquaton(equation)
        self.lexicalBuilder = None
    @staticmethod
    def massageEquaton(equation):
        equation = equation.replace("(", "({")
        equation = equation.replace("({{", "({")
        equation = equation.replace(")", "})")
        equation = equation.replace("}})", "})")
        return equation

    def test(self):
        latex = r"""\textbf{Hi there!} Here is \emph{an equation
                \begin{equation}
                \zeta = x + i y
                \end{equation}
                where $i$ is the imaginary unit.
                """
        return LatexNodes2Text().latex_to_text(latex)

    def test2(self):
        w = LatexWalker(r"""\[\int_{a}^{b} x^2 \,dx \]""")
        (nodelist, pos, len_) = w.get_latex_nodes(pos=0)

        for i in range(len(nodelist[0].nodelist)):
            print(nodelist[0].nodelist[i])

    def traverseLatex(self, text):
        w = LatexWalker(text)
        (nodelist, pos, len_) = w.get_latex_nodes(pos=0)

        self._traverseLatex(nodelist)

    def _traverseLatex(self, nodelist, depth=0, space="   "):
        if nodelist != None:
            for i in range(len(nodelist)):
                if hasattr(nodelist[i], 'nodelist'):
                    self._traverseLatex(
                        nodelist[i].nodelist, depth + 1, space + "    ")

    def findMathNode(self):
        w = LatexWalker(self.equation)
        (nodelist, pos, len_) = w.get_latex_nodes(pos=0)
        return self._findMathNodeInList(nodelist)

    def getNextNode(self, parentNode, current):
        return parentNode.nodelist[current + 1]

    def getNodeAt(self, parentNode, current):
        return parentNode.nodelist[current]

    def _findMathNodeInList(self, nodelist):
        for i in range(len(nodelist)):
            mathNode = self._findMathNode(nodelist[i])
            if mathNode != None:
                return mathNode
        return None

    def _findMathNode(self, node):
        if isinstance(node, LatexMathNode):
            return node
        if hasattr(node, 'nodelist'):
            if node.nodelist != None:
                for i in range(len(node.nodelist)):
                    return self._findMathNode(node.nodelist[i])
        return None

    def addToStack(self, stack, previousNode, currentNode):
        if currentNode == None:
            raise Exception("current node cant be none")
        stack.append({'pn': previousNode, 'ln': currentNode})

    def buildTree(self, mathNode):
        if mathNode == None:
            raise Exception("math node is none, buildTree")
        currentNode = None
        previousNode = None
        stack = []
        opened = None
        opened_list = []
        for i in range(len(mathNode.nodelist)):
            nextNode = self.getNodeAt(mathNode, i)
            remaining = None
            while remaining == None or remaining != "":
                stack_context = self.getStackContext(stack)
                currentNode, remaining = self.buildNode(
                    nextNode, currentNode, remaining, stack_context)

                if currentNode.isOpeningDelimeter():
                    opened = True
                    continue
                if currentNode.isClosingDelimiter():
                    opened = False
                    currentNode = self.buildGroup(opened_list)
                    currentNode = self.buildContextNode(currentNode)
                    opened_list = []
                if opened:
                    opened_list.append(nextNode)
                    continue
                if currentNode.getTokenType() == TokenType.S_SPACE:
                    continue
                if len(stack) > 0:
                    popStackAgain = True
                    while popStackAgain:
                        popStackAgain = False
                        peekTop = self.peekStack(stack)
                        if peekTop == None:
                            self.addToStack(
                                stack, previousNode, currentNode)
                        elif peekTop.lookBehind():
                            if currentNode.isClosing() or peekTop.isGreedy():
                                if currentNode.isClosing():
                                    currentNode = self.lexicalBuilder.parse(
                                        peekTop, currentNode)
                                elif peekTop.isGreedy():
                                    currentNode = self.lexicalBuilder.parse(
                                        peekTop, currentNode)

                                self.restack(stack, currentNode)
                                peekTop = self.peekStack(stack)
                                if peekTop.isClosing():
                                    popStackAgain = True
                                    currentNode = self.peekStack(stack)
                                    self.popStack(stack)
                            else:
                                self.addToStack(
                                    stack, previousNode, currentNode)
                        elif currentNode.lookAhead():
                            currentNode = self.lexicalBuilder.parse(
                                currentNode, peekTop)
                            self.restack(stack, currentNode)
                            peekTop = self.peekStack(stack)
                            if peekTop.isClosing():
                                popStackAgain = True
                                currentNode = self.peekStack(stack)
                                self.popStack(stack)
                        else:
                            self.addToStack(
                                stack, previousNode, currentNode)
                else:
                    self.addToStack(stack, previousNode, currentNode)

                previousNode = currentNode
        if len(stack) > 0:
            if len(stack) == 1:
                return self.getClimbToRoot(currentNode)
            currentNode = None
            while len(stack) > 0:
                stackItem = self.popStack(stack)
                if currentNode == None:
                    currentNode = stackItem['ln']
                else:
                    currentNode = self.lexicalBuilder.buildContextualMultiply(
                        currentNode, stackItem['ln'])
        return self.getClimbToRoot(currentNode)

    def buildContextualMultiplyFromStack(self, stack, node):
        result = node
        done = False
        while not done:
            done = True
            if len(stack) > 0:
                top = stack[-1]
                lastNode = top['ln']

    def peekStack(self, stack):
        if len(stack) > 0:
            return stack[-1]["ln"]
        return None

    def popStack(self, stack):
        if len(stack) > 0:
            return stack.pop()
        raise Exception("cant pop an empty stack")

    def restack(self, stack, node):
        if len(stack) > 0:
            stack[-1]['ln'] = node
            return
        raise Exception("cant restack if the stack is empty")

    def createNewSelfClosing(self, node):
        if node.getTokenType() == TokenType.T_INTEGRAL:
            result = Node(TokenType.S_DELIMITER)
            self.lexicalBuilder.handleSyntaxDelimeter(result, node)
            return result
        raise Exception('unable to create a new delimiter')

    def satifyNode(self, node, part):
        if node.getTokenType() == TokenType.S_DELIMITER:
            potentials = node.getPotentials()
            for p in potentials:
                if self.matchesPotential(part, p):
                    return self.transformMatch(node, part, p)
        raise Exception("unable to satify node")

    # Transforms the part to the new node of the satifying type
    # Then sets the part as the satisfying node for the delimiting node.
    # Then it should be possible to pop the node from the stack
    def transformMatch(self, node, part, p):
        if p == TokenType.T_RANGE:
            if part.getTokenType() == TokenType.T_POWER:
                part.changeTokenType(TokenType.T_RANGE)
                part.changeChildKey(LexicalRuleItem.K_LEFT,
                                    LexicalRuleItem.K_START)
                part.changeChildKey(LexicalRuleItem.K_RIGHT,
                                    LexicalRuleItem.K_END)
                node.setSatisfyingNode(part)
                return part
        raise Exception("unable to transform match")

    def matchesPotential(self, part, p):
        if p == TokenType.T_RANGE:
            if part.getTokenType() == TokenType.T_POWER:
                return True
        return False

    def getStackContext(self, stack):
        if stack != None:
            if len(stack) > 0:
                lastItem = stack[-1]
                ln = lastItem['ln']
                return ln
        return None

    def getClimbToRoot(self, node):
        root = node
        result = root
        while root != None:
            root = root.getParent()
            if root != None:
                result = root

        return result

    def makeContextNode(self,  middle):
        node = Node(TokenType.T_CONTEXT)
        node.addChild(LexicalRuleItem.K_MIDDLE, middle)
        return node

    def buildNode(self, node, previousNode=None, remainingText=None, stack_context=None):
        if self.lexicalBuilder == None:
            self.lexicalBuilder = LexicalBuilder()
            self.lexicalBuilder.setEqBuilder(self)
        return self.lexicalBuilder.consume(node, previousNode, remainingText, stack_context)

    def buildGroup(self, nodelist):
        if self.lexicalBuilder == None:
            self.lexicalBuilder = LexicalBuilder()
            self.lexicalBuilder.setEqBuilder(self)
        return self.lexicalBuilder.buildGroup(nodelist)

    def buildContextNode(self, node):
        return self.makeContextNode(node)

    def printLatexNodes(self, text):
        print("print " + text)
        w = LatexWalker(text)

        (nodelist, pos, len_) = w.get_latex_nodes(pos=0)
        print("len_ " + str(len_))
        self._printLatexNodes(nodelist)

    def _printLatexNodes(self, nodelist, depth=0, space="   "):
        if nodelist != None:
            for i in range(len(nodelist)):
                print(nodelist[i])
                if hasattr(nodelist[i], 'nodelist'):
                    self._printLatexNodes(
                        nodelist[i].nodelist, depth + 1, space + "    ")
