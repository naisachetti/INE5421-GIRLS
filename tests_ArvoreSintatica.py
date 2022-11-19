import unittest
from ArvoreSintatica import *

class VerificarArvoreSintatica(unittest.TestCase):
    # Testa se AS esta sendo montada corretamente
    def test_get_arvore(self):
        # Arrange
        regex = "(.(.(.(*(+ a b)) a) b) b)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.get_arvore()

        # Assert
        self.assertEqual("(.(.(.(.(*(+ab))a)b)b)#)", arvore)

    # Testa se AS esta sendo montada corretamente
    def test2_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) a)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.get_arvore()

        # Assert
        self.assertEqual("(.(+(.(*(+ab))(.ab))a)#)", arvore)

    # Testa se AS esta sendo montada corretamente
    def test3_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) &)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.get_arvore()

        # Assert
        self.assertEqual("(.(+(.(*(+ab))(.ab))&)#)", arvore)

    # Testa se calculo dos anulaveis esta correto
    def test4_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) &)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(anulaveis=True)

        # Assert
        self.assertEqual("(.(+{n}(.(*{n}(+ab))(.ab))&{n})#)", arvore)
        print(arvore)
