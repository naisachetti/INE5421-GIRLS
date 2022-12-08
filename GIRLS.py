from Gramatica import Gramatica
from Parser import AnalisadorSintatico
from Lexer import AnalisadorLexico

class GIRLS:
    def __init__(self, folder):
        self.lexer = AnalisadorLexico(folder)
        self.parser = AnalisadorSintatico(folder, self.lexer)

        self.parser.parse(True)

if __name__ == '__main__':
    girls = GIRLS('pasca')
