from Automato import *

from functools import reduce
from glob import glob

class AnalisadorLexico:
    def __init__(self):
        self.tokens = None
        self.automato = None
        self.tabela = []

    def from_file(self, path):
        path = path
        ers = glob(path + '/*.er')

        autos = [Automato().from_regex(er) for er in ers]
        self.automato = reduce(Automato.uniao_com, autos[1:], autos[0])

    def gerar_tokens(self, source_path):
        with open(source_path, 'r') as file:
            chars = list(file.read())
        begin = 0
        forward = 1
        while forward <= len(chars):
            if chars[begin] not in [' ','\n', '\t', '\r']:
                lexeme0 = ''.join(chars[begin:forward])
                lexeme1 = ''.join(chars[begin:forward+1])

                if self.automato.reconhece(lexeme1):
                    forward += 1
                else:
                    print(lexeme0)
                    self.tabela.append((lexeme0, self.automato.token(lexeme0)[0]))
                    begin = forward
                    forward = begin + 1
            else:
                begin += 1
                forward = begin + 1


al = AnalisadorLexico()
al.from_file('demoniC')
al.gerar_tokens('demoniC/program')
print(al.tabela)
