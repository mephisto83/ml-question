import unittest
from lexicalbuilderrules import LexicalBuilderRule
from lexicalruleitem import LexicalRuleItem
from nodetype import TokenType
from node import Node
class TestEquationData(unittest.TestCase):

    def test_MultiplyRule(self):
        data = LexicalBuilderRule.multiplyRule()
        self.assertNotEqual(data, None, "multiply rule was none")
        self.assertEqual(data.expectedItemOrder[0], LexicalRuleItem.K_LEFT)
    def test_sortOperations(self):
        data = LexicalBuilderRule.multiplyRule()
        multiplyNode = Node(TokenType.T_MULT)
        subtractNode = Node(TokenType.T_MINUS)
        order = data.sortOperations([subtractNode, multiplyNode])
        self.assertEqual(order[0], multiplyNode)
    def test_swapLeftRight(self):
        data = LexicalBuilderRule.multiplyRule()
        multiplyNode = Node(TokenType.T_MULT)
        subtractNode = Node(TokenType.T_MINUS)
        num = Node(TokenType.T_NUM, "4")
        num2 = Node(TokenType.T_NUM, "5")
        num3 = Node(TokenType.T_NUM, "6")
        subtractNode.addChild(LexicalRuleItem.K_LEFT, num)
        subtractNode.addChild(LexicalRuleItem.K_RIGHT, num2)
        data.swapLeftRight(subtractNode, multiplyNode)
if __name__ == '__main__':
    unittest.main()