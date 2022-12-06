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

        self.automato = reduce(Automato.uniao_com, autos, autos[0]).determinizado().rename()

    def gerar_tokens(self, source_path):
        with open(source_path, 'r') as file:
            chars = list(file.read())
        begin = 0
        forward = 5
        lexeme = ''.join(chars[begin:forward])
        while True:




al = AnalisadorLexico()
al.from_file('bnm')
al.gerar_tokens('bnm/program')
