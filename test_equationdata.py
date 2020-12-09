from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import LatexWalker, LatexCharsNode, LatexEnvironmentNode, LatexMacroNode, LatexMathNode
import unittest
from node import Node
from nodetype import TokenType
from equationdata import EquationData
from lexicalruleitem import LexicalRuleItem

class TestEquationData(unittest.TestCase):

    def test_TraverseLatex(self):
        data = EquationData("equation")
        data.traverseLatex(r"""\[ \intop{a}^{b} x^2 \,\delta x \]""")

    def test_getMathNode(self):
        data = EquationData(r"""\[3\times4\]""")
        mathNode = data.findMathNode()
        self.assertNotEqual(mathNode, None, "Should find a math node")
    
    def test_consumeMathNode(self):
        data = EquationData(r"""\[3\times4\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNextNode(mathNode, -1)
        self.assertEqual(True, isinstance(nextNode, LatexCharsNode))
    
    def test_buildNode(self):
        data = EquationData(r"""\[3\times4\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNextNode(mathNode, -1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
    def test_cos(self):
        data = EquationData(r"""\[\cos\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNextNode(mathNode, -1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
    
    def test_integral_with_func(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNextNode(mathNode, -1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_INTEGRAL)
    
    def test_range_with_func(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.S_VERTICAL)
            
    def test_GROUP_with_func(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 2)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_VARIABLE)

    def test_power_with_func(self):
        data = EquationData(r"""\[{a}^{b}\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_POWER)
    def test_delta(self): 
        data = EquationData(r"""\[\delta\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_DELTA)
        
    def test_sin(self):
        data = EquationData(r"""\[\sin\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNextNode(mathNode, -1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
    def test_tan(self):
        data = EquationData(r"""\[\tan\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNextNode(mathNode, -1)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")

    def test_LeftParanMacro(self):
        data = EquationData(r"""\[\lparen\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_LPAR)
        
    def test_RightParenMacro(self):
        data = EquationData(r"""\[\rparen\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, _ = data.buildNode(nextNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_RPAR)
        
    
    def test_buildTree(self):
        data = EquationData(r"""\[3\times4\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)
        
    def test_buildTree_withparens_no_mutiply(self):
        data = EquationData(r"""\[3\lparen4\rparen\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)

    def test_buildTree_withparens_reversed_no_mutiply(self):
        data = EquationData(r"""\[\lparen4\rparen3\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)
        
    def test_buildTree_withparens_reversed_with_mutiply(self):
        data = EquationData(r"""\[{4}\times3\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)

    def test_buildTree_with_double_parens_reversed_no_mutiply(self):
        data = EquationData(r"""\[{{4}}3\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)

    def test_buildTree_3X4X5(self):
        data = EquationData(r"""\[3\times4\times5\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)
        
    def test_buildTree_with_expression(self):
        data = EquationData(r"""\[\cos\lparen4\rparen\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_COS)
        left = res.hasChild(LexicalRuleItem.K_PARAM1)
        self.assertTrue(left)
    def test_buildTree_with_number(self):
        data = EquationData(r"""\[\cos4\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_COS)
        left = res.hasChild(LexicalRuleItem.K_PARAM1)
        self.assertTrue(left)
    def test_buildTree_with_sin_number(self):
        data = EquationData(r"""\[\sin4\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_SIN)
        left = res.hasChild(LexicalRuleItem.K_PARAM1)
        self.assertTrue(left)
    def test_buildTree_3MINUS4X5(self):
        data = EquationData(r"""\[3-4\times5\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MINUS)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)
    def test_buildTree_3x4MINUS5(self):
        data = EquationData(r"""\[3\times4-5\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MINUS)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)
    def test_ab_multiply(self):
        data = EquationData(r"""\[ab\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        right = res.hasChild(LexicalRuleItem.K_RIGHT)
        self.assertTrue(left)
        self.assertTrue(right)
    
    def test_delta_with_respect(self): 
        data = EquationData(r"""\[\{delta x}\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_DELTA)
        left = res.hasChild(LexicalRuleItem.K_WITH_RESPECT)
        self.assertTrue(left)
    def test_delta_with_respect(self): 
        data = EquationData(r"""\[{\delta x}y\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        self.assertTrue(left)
    def test_y_times_delta_x(self): 
        data = EquationData(r"""\[y{\delta x}\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        self.assertTrue(left)
        left = res.getChild(LexicalRuleItem.K_LEFT)
        self.assertEqual(left.getTokenType(), TokenType.T_VARIABLE)
        right = res.getChild(LexicalRuleItem.K_RIGHT)
        self.assertEqual(right.getTokenType(), TokenType.T_DELTA)
    def test_P_y_P_times_delta_x(self): 
        data = EquationData(r"""\[{\lparen y\rparen}{\delta x}\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_MULT)
        left = res.hasChild(LexicalRuleItem.K_LEFT)
        self.assertTrue(left)
        left = res.getChild(LexicalRuleItem.K_LEFT)
        self.assertEqual(left.getTokenType(), TokenType.T_VARIABLE)
        right = res.getChild(LexicalRuleItem.K_RIGHT)
        self.assertEqual(right.getTokenType(), TokenType.T_DELTA)
    

    def test_integral_with_func(self):
        data = EquationData(r"""\[\int_{a}^{b} {x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertIsNotNone(res, "Build node should return a node")
        self.assertEqual(res.getTokenType(), TokenType.T_INTEGRAL)
        self.assertEqual(res.getChild(LexicalRuleItem.K_MIDDLE).getTokenType(), TokenType.T_POWER)
        self.assertEqual(res.getChild(LexicalRuleItem.K_RANGE).getTokenType(), TokenType.S_VERTICAL)
    def test_integral_is_delimiter(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, remaining = data.buildNode(nextNode, None, None, None)
        self.assertFalse(res.isDelimiter(), "an integral is not a delimiter in an empty stack")
    def test_vertial_input_is_delimiter(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        stack = []
        nextNode = data.getNodeAt(mathNode, 0)
        res, remaining = data.buildNode(nextNode, None, None, None)
        node = Node(TokenType.S_VERTICAL)
        data.addToStack(stack, res, node)
        self.assertTrue(node.isDelimiter(), "latex vertical is a delimeter")

    def test_vertial_input_is_delimiter(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        stack = []
        nextNode = data.getNodeAt(mathNode, 0)
        res, remaining = data.buildNode(nextNode, None, None, None)
        nextNode = data.getNodeAt(mathNode, 1)
        node, remaining = data.buildNode(nextNode, None, None, None)
        data.addToStack(stack, res, node)
        self.assertTrue(node.isOpeningDelimeter([], res), "latex vertical is an opening delimeter")

    def test_if_integral_is_full(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        stack = []
        nextNode = data.getNodeAt(mathNode, 0)
        res, remaining = data.buildNode(nextNode, None, None, None)
        self.assertFalse(res.isClosing(), "latex vertical is an opening delimeter")
        

    def test_vertial_input_is_delimiter(self):
        data = EquationData(r"""\[\int_{a}^{b}{x^2}{\delta x}\]""")
        mathNode = data.findMathNode()
        stack = []
        nextNode = data.getNodeAt(mathNode, 0)
        res, remaining = data.buildNode(nextNode, None, None, None)
        node = Node(TokenType.S_VERTICAL)
        data.addToStack(stack, res, node)
        self.assertFalse(node.isDelimiter(), "latex vertical is a delimeter")
    def test_integral_is_not_closing_empty(self):
        data = EquationData(r"""\[\int_{a+1}^{b}{{x+1}^{2c}}{\delta x}\]""")
                                # \int_{a+1}^{b}{{x+1}^{2c}+x^{2c}}{\delta x}
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, remaining = data.buildNode(nextNode, None, None, None)
        self.assertFalse(res.isClosing())
    def test_vertial_input_is_closing(self):
        data = EquationData(r"""\[\int_{a+1}^{b}{{x+1}^{2c}}{\delta x}\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 1)
        res, remaining = data.buildNode(nextNode, None, None, None)
        self.assertEqual(res.getTokenType(), TokenType.S_VERTICAL)
        self.assertFalse(res.isClosing())
    def test_plus_returns(self):
        data = EquationData(r"""\[+\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, _ = data.buildNode(nextNode, None, None, None)
        self.assertEqual(res.getTokenType(), TokenType.T_PLUS)
        self.assertFalse(res.isClosing())
        self.assertTrue(res.lookAhead())
        self.assertTrue(res.lookBehind())
    def test_avaraible_returns(self):
        data = EquationData(r"""\[a\]""")
        mathNode = data.findMathNode()
        nextNode = data.getNodeAt(mathNode, 0)
        res, _ = data.buildNode(nextNode, None, None, None)
        self.assertEqual(res.getTokenType(), TokenType.T_VARIABLE)
        self.assertTrue(res.isClosing())
        self.assertFalse(res.lookAhead())
        self.assertFalse(res.lookBehind())
    def test_a_plus_(self):
        data = EquationData(r"""\[a+\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertEqual(res.getTokenType(), TokenType.T_PLUS)
        self.assertTrue(res.hasChild(LexicalRuleItem.K_LEFT))
    def test_a_plus_b_(self):
        data = EquationData(r"""\[a+b\]""")
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        self.assertEqual(res.getTokenType(), TokenType.T_PLUS)
        self.assertTrue(res.hasChild(LexicalRuleItem.K_LEFT))
        self.assertTrue(res.hasChild(LexicalRuleItem.K_RIGHT))
        
        
 
if __name__ == '__main__':
    unittest.main()