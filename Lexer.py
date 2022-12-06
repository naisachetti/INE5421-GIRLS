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
        for auto in autos:
            print(auto)
        self.automato = reduce(Automato.uniao_com, autos[1:], autos[0]).determinizado().rename()
        print(self.automato)

    def gerar_tokens(self, source_path):
        with open(source_path, 'r') as file:
            chars = list(file.read())
        begin = 0
        forward = 1

        while forward <= len(chars):
            if chars[begin] not in [' ','\n']:
                lexeme = ''.join(chars[begin:forward])
                next = ''.join(chars[begin:forward+1])
                while not self.automato.reconhece(lexeme) or self.automato.reconhece(next):
                    forward += 1
                    lexeme = ''.join(chars[begin:forward])
                    next = ''.join(chars[begin:forward+1])
                    print(lexeme, next)

                self.tabela.append((lexeme, self.automato.token(lexeme)[0]))
                begin = forward
                forward = begin + 1
            else:
                begin += 1
                forward = begin + 1


al = AnalisadorLexico()
al.from_file('bnm')
#al.gerar_tokens('bnm/prog1')
print(al.tabela)
