import sys

from Gramatica import Gramatica
from Parser import AnalisadorSintatico
from Lexer import AnalisadorLexico

class GIRLS:
    def __init__(self, folder):
        self.lexer = AnalisadorLexico(folder)
        self.parser = AnalisadorSintatico(folder, self.lexer)
        if self.parser.parse(True):
            print("\nSintaxe e léxico correto do arquivo program")
        else:
            print("\nProblema na sintaxe")

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('Informe o nome da pasta')
    else:
        girls = GIRLS(sys.argv[1])
