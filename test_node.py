import unittest
from node import Node
from nodetype import TokenType

class TestEquationData(unittest.TestCase):

    def test_NodeCreate(self):
        data = Node(TokenType.T_NUM)
        self.assertNotEqual(data, None, "node is not None")
    def test_AddChild(self):
        data = Node(TokenType.T_DIV)
        numberNode = Node(TokenType.T_NUM)
        data.addChild("left", numberNode)
        self.assertEqual(numberNode, data.children["left"])
    def test_hasChild_hasno(self):
        data = Node(TokenType.T_PLUS)
        self.assertEqual(data.hasChild(TokenType.T_PLUS), False)
    def test_hasChild_has(self):
        data = Node(TokenType.T_PLUS)
        num = Node(TokenType.T_NUM, "4")
        data.addChild(TokenType.T_PLUS, num)
        self.assertEqual(data.hasChild(TokenType.T_PLUS), True)
    def test_node_has_id(self):
        data = Node(TokenType.T_CONTEXT)
        self.assertNotEqual(None, data.id)
if __name__ == '__main__':
    unittest.main()