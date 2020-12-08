from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexMathNode
from lexicalbuilder import LexicalBuilder
from lexicalbuilderrules import LexicalBuilderRule
from nodetype import TokenType
from node import Node
from lexicalruleitem import LexicalRuleItem


class EquationData:
    def __init__(self, equation):
        self.equation = equation
        self.lexicalBuilder = None

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

    def buildTree(self, mathNode):
        if mathNode == None:
            raise Exception("math node is none, buildTree")
        currentNode = None
        previousNode = None
        stack = []
        for i in range(len(mathNode.nodelist)):
            nextNode = self.getNodeAt(mathNode, i)
            remaining = None
            while remaining == None or remaining != "":
                stack_context = self.getStackContext(stack)
                currentNode, remaining = self.buildNode(
                    nextNode, currentNode, remaining, stack_context)
                if currentNode.isClosingSelf():
                    topNode = stack[-1]
                    pn = topNode['pn']
                    ln = topNode['ln']
                    if LexicalBuilderRule.isNodeFull(previousNode):
                        nodeForPrevious = self.satifyNode(ln, previousNode)
                        stack.pop()
                        topNode = stack[-1]
                        pn = topNode['pn']
                        ln = topNode['ln']
                        if ln == None:
                            pass
                        elif ln.isOperator():
                            currentNode = self.lexicalBuilder.parse(
                                ln, nodeForPrevious)
                        else:
                            currentNode = self.lexicalBuilder.buildContextualMultiply(
                                nodeForPrevious, ln)
                        if not LexicalBuilderRule.isNodeFull(currentNode):
                            selfClosingNode = self.createNewSelfClosing(currentNode)
                            stack.append({'pn': currentNode, 'ln': selfClosingNode})
                            currentNode = selfClosingNode

                elif currentNode.isSelfClosing():
                    if currentNode.isClosing():  # if the node has all the required inputs
                        topNode = stack.pop()
                        pn = topNode['pn']
                        ln = topNode['ln']
                        if pn == None:
                            pass
                        elif pn.isOperator():
                            currentNode = self.lexicalBuilder.parse(pn, ln)
                        else:
                            currentNode = self.lexicalBuilder.buildContextualMultiply(
                                ln, pn)
                    else:
                        stack.append({'pn': previousNode, 'ln': currentNode})
                elif currentNode.isDelimeter():
                    if currentNode.isOpeningDelimeter():
                        stack.append({'pn': previousNode, 'ln': currentNode})
                        currentNode = None
                    else:
                        topNode = stack.pop()
                        pn = topNode['pn']
                        ln = topNode['ln']
                        if previousNode == None:
                            raise Exception(
                                "there shouldnt be an undefined middle to a context")
                        contextNode = self.makeContextNode(
                            ln, previousNode, currentNode)
                        if pn == None:
                            currentNode = contextNode
                        elif pn.isOperator():
                            currentNode = self.lexicalBuilder.parse(
                                pn, contextNode)
                        else:
                            currentNode = self.lexicalBuilder.buildContextualMultiply(
                                contextNode, pn)
                previousNode = currentNode
        if len(stack) > 0:
            raise Exception("stack should be empty on exit, equation data")

        return self.getClimbToRoot(currentNode)
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

    def makeContextNode(self, leftDelimiter, middle, rightDelimiter):
        node = Node(TokenType.T_CONTEXT)
        node.addChild(LexicalRuleItem.K_LEFT, leftDelimiter)
        node.addChild(LexicalRuleItem.K_MIDDLE, middle)
        node.addChild(LexicalRuleItem.K_RIGHT, rightDelimiter)
        return node

    def buildNode(self, node, previousNode=None, remainingText=None, stack_context=None):
        if self.lexicalBuilder == None:
            self.lexicalBuilder = LexicalBuilder()
            self.lexicalBuilder.setEqBuilder(self)
        return self.lexicalBuilder.consume(node, previousNode, remainingText, stack_context)

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
