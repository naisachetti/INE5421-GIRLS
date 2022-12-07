from Gramatica import Gramatica
from Parser import AnalisadorSintatico
from Lexer import AnalisadorLexico

class GIRLS:
    def __init__(self, folder):
        self.lexer = AnalisadorLexico(folder)

        gramatica = Gramatica().from_file(folder + '/grammar').tratada()
        self.parser = AnalisadorSintatico(gramatica)
        self.parser.validate(gramatica)

        self.parser.parse(self.lexer, True)

if __name__ == '__main__':
    girls = GIRLS('default')
