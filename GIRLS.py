import sys

from Gramatica import Gramatica
from Parser import AnalisadorSintatico
from Lexer import AnalisadorLexico

class GIRLS:
    def __init__(self, folder, nome_programa=""):
        self.lexer = AnalisadorLexico(folder, nome_programa)
        self.parser = AnalisadorSintatico(folder, self.lexer, validar=False, precompiled=True)
        if self.parser.parse(True):
            print("\nSintaxe e léxico correto do arquivo program")
        else:
            print("\nProblema na sintaxe")
            raise SyntaxError()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Informe o nome da pasta')
    else:
        if len(sys.argv) >= 3:
            girls = GIRLS(sys.argv[1], sys.argv[2])
        else:
            girls = GIRLS(sys.argv[1])
