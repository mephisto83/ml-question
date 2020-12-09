import unittest
from lexicalbuilder import LexicalBuilder
from nodetype import TokenType
import re 

class TestEquationData(unittest.TestCase):

    def test_CreateLexicalBuilder(self):
        data = LexicalBuilder()
        self.assertNotEqual(data, None)

    def test_parseString(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('4')
        self.assertEqual(len(remaingString), 0, "there should be no more string")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_NUM, "The node should be a number")
    def test_getTokenType(self):
        data = LexicalBuilder()
        token_type = data.getTokenType('4')
        self.assertEqual(token_type, TokenType.T_NUM)
    def test_getNumberTypeOfMultidigitNumber(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('54')
        self.assertEqual(len(remaingString), 0, "there should be no more string")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_NUM, "The node should be a number")

    def test_getCombination(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('54+')
        self.assertEqual(len(remaingString), 1, "there should be 1 more char left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_NUM, "The node should be a number")
        
    def test_54plus4(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('54+4')
        self.assertEqual(len(remaingString), 2, "there should be more string left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_NUM, "The node should be a number")
    def test_54plus4minus4(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('54+4-4')
        self.assertEqual(len(remaingString), 4, "there should be more string left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_NUM, "The node should be a number")
    def test_54plus4minus4_DONTignorespace(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('54 + 4-4')
        self.assertEqual(len(remaingString), 6, "there should be more string left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_NUM, "The node should be a number")
    def test_justplust_(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('+')
        self.assertEqual(len(remaingString), 0, "there should be no more strings left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_PLUS, 'The result should be a plus')
    def test_justplust_five(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('+5')
        self.assertEqual(len(remaingString), 1, "there should a 5 left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_PLUS, 'The result should be a plus')
    def test_leftparen(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString('(')
        self.assertEqual(len(remaingString), 0, "there should a 0 left")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_LPAR, 'The result should be a left parenthesis')
    def test_rightparen(self):
        data = LexicalBuilder()
        remaingString, lastNode = data.produceNodeFromString(')')
        self.assertEqual(len(remaingString), 0, "there should a 0 right")
        self.assertEqual(lastNode.getTokenType(), TokenType.T_RPAR, 'The result should be a right parenthesis')
    

if __name__ == '__main__':
    unittest.main()