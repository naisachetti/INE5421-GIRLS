from Automato import *
from regex_lib import read_regex

from functools import reduce
from operator import iconcat
from glob import glob

class AnalisadorLexico:
    def __init__(self, folder):
        self.folder = folder
        self.automato = None
        self.tabela = []
        self.from_file()
        self.analisar()

    def from_file(self):
        tokens_path = self.folder + '/tokens'

        tokens_regex = read_regex(tokens_path)
        autos = [Automato().from_regex(tokens_regex[token], token) for token in tokens_regex.keys()]
        self.automato = reduce(Automato.uniao_com, autos)

    def analisar(self):
        source = self.folder + '/program'
        with open(source, 'r') as file:
            code = file.read()

        for char in ["\n", '\t', '\r']:
            code = code.replace(char, ' ')

        def tokens(word):
            tokens = []
            begin = 0
            forward = 1
            try:
                while forward <= len(word):
                    lexeme = word[begin:forward]
                    next = word[begin:forward+1]
                    while (not self.automato.reconhece(lexeme) or self.automato.reconhece(next)) and forward <= len(word):
                        forward += 1
                        lexeme = word[begin:forward]
                        next = word[begin:forward+1]
                    tokens.append((self.automato.token(lexeme), lexeme))
                    begin = forward
                    forward = begin + 1
            except KeyError:
                raise Exception(f"Lexema {lexeme} não faz parte da linguagem")

            return tokens

        self.tabela = reduce(iconcat, map(tokens, code.split()))

    def to_csv(self):
        with open(self.folder+'/lexer.csv', 'w') as csv:
            for item in self.tabela:
                csv.write(f"{item[0]},{item[1]}\n")


    def gerador(self):
        for item in self.tabela:
            yield item[0]

if __name__ == '__main__':
    al = AnalisadorLexico('portugues')
    al.to_csv()
