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

    # Testa se calculo dos firstpos esta correto
    def test4_get_arvore(self):
        # Arrange
        regex = "(.(.(.(*(+ a b)) a) b) b)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(firstpos=True)

        # Assert
        self.assertEqual("(.{1,2,3}(.{1,2,3}(.{1,2,3}(.{1,2,3}(*{1,2}(+{1,2}a{1}b{2}))a{3})b{4})b{5})#{6})", arvore)

    # Testa se calculo dos firstpos esta correto
    def test5_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) a)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(firstpos=True)

        # Assert
        self.assertEqual("(.{1,2,3,5}(+{1,2,3,5}(.{1,2,3}(*{1,2}(+{1,2}a{1}b{2}))(.{3}a{3}b{4}))a{5})#{6})", arvore)

    # Testa se calculo dos firstpos esta correto
    def test6_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) &)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(firstpos=True)

        # Assert
        self.assertEqual("(.{1,2,3,6}(+{1,2,3}(.{1,2,3}(*{1,2}(+{1,2}a{1}b{2}))(.{3}a{3}b{4}))&{})#{6})", arvore)

    # Testa se calculo dos lastpos esta correto
    def test7_get_arvore(self):
        # Arrange
        regex = "(.(.(.(*(+ a b)) a) b) b)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(lastpos=True)

        # Assert
        self.assertEqual("(.{6}(.{5}(.{4}(.{3}(*{1,2}(+{1,2}a{1}b{2}))a{3})b{4})b{5})#{6})", arvore)

    # Testa se calculo dos lastpos esta correto
    def test8_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) a)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(lastpos=True)

        # Assert
        self.assertEqual("(.{6}(+{4,5}(.{4}(*{1,2}(+{1,2}a{1}b{2}))(.{4}a{3}b{4}))a{5})#{6})", arvore)

    # Testa se calculo dos lastpos esta correto
    def test9_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) &)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(lastpos=True)

        # Assert
        self.assertEqual("(.{6}(+{4}(.{4}(*{1,2}(+{1,2}a{1}b{2}))(.{4}a{3}b{4}))&{})#{6})", arvore)

    # Testa se calculo dos followpos esta correto
    def test10_get_arvore(self):
        # Arrange
        regex = "(.(.(.(*(+ a b)) a) b) b)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(followpos=True)

        # Assert
        self.assertEqual("(.(.(.(.(*(+a{1,2,3}b{1,2,3}))a{4})b{5})b{6})#{})", arvore)

    # Testa se calculo dos followpos esta correto
    def test11_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) a)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(followpos=True)

        # Assert
        self.assertEqual("(.(+(.(*(+a{1,2,3}b{1,2,3}))(.a{4}b{6}))a{6})#{})", arvore)

    # Testa se calculo dos followpos esta correto
    def test12_get_arvore(self):
        # Arrange
        regex = "(+(.(*(+ab)) (. a b)) &)"
        a_sint = ArvoreSintatica(regex)

        # Act
        arvore = a_sint.calcula_infos_nodos()
        arvore = a_sint.get_arvore(followpos=True)

        # Assert
        self.assertEqual("(.(+(.(*(+a{1,2,3}b{1,2,3}))(.a{4}b{6}))&{})#{})", arvore)