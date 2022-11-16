import unittest
from ArvoreSintatica import *

class VerificarArvoreSintatica(unittest.TestCase):
    def test_get_arvore(self):
        # Arrange
        regex = "(.(.(.(*(+ a b)) a) b) b)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.get_arvore()

        # Assert
        self.assertEqual("(.(.(.(.(*(+ab))a)b)b)#)", arvore)

    def test2_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) a)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.get_arvore()

        # Assert
        self.assertEqual("(.(+(.(*(+ab))(.ab))a)#)", arvore)