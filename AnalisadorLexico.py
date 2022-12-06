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
        self.automato = reduce(Automato.uniao_com, autos, autos[0]).determinizado().rename()
        print(self.automato)


AnalisadorLexico().from_file('bnm')
