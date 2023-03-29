from Automato import *
from regex_lib import read_regex

from functools import reduce
from operator import iconcat
import sys

class AnalisadorLexico:
    def __init__(self, folder):
        self.folder = folder
        self.automato = None
        self.tabela = []
        self.from_file()
        self.analisar()

    # Pega o arquivo 'tokens' e monta o automâto que reconhece a linguagem a partir das definições no arquivo
    def from_file(self):
        tokens_path = self.folder + '/tokens'

        # Le o arquivo de definições regulares e tokens
        tokens_regex = read_regex(tokens_path)
        # Cria os automâtos a partir das regex
        autos = [Automato().from_regex(tokens_regex[token], token) for token in tokens_regex.keys()]
        # Faz a união dos automâtos
        self.automato = reduce(Automato.uniao_com, autos)
        # Escreve o automâto em um arquivo
        self.automato.to_file(self.folder + '/automata')

    # Analisa o arquivo 'program'
    def analisar(self):
        source = self.folder + '/program'
        with open(source, 'r') as file:
            code = file.read()

        # Substitui caracteres especiais por espaços
        for char in ["\n", '\t', '\r']:
            code = code.replace(char, ' ')

        # Obtem todos os tokens de uma string
        def tokens(word):
            tokens = []
            begin = 0
            forward = 1
            max_forward = 10
            try:
                while forward <= len(word):
                    lexeme = word[begin:forward]
                    next = [word[begin:forward+i+1] for i in range(max_forward)]
                    # Enquanto (não reconhecer o lexema ou reconhecer o lexema adicionado de um caractere)
                    # e não passamos do fim da palavra

                    while (not self.automato.reconhece(lexeme) or any(map(self.automato.reconhece, next))) \
                            and forward <= len(word):
                        forward += 1
                        lexeme = word[begin:forward]
                        next = [word[begin:forward+i+1] for i in range(max_forward)]
                    tk = self.automato.token(lexeme)
                    tokens.append((tk, lexeme))
                    print(f'{tk:>10} {lexeme}')
                    begin = forward
                    forward = begin + 1
            # Caso o automâto não tenha uma transição, o lexema não faz parte da linguagem
            except KeyError:
                print(f'Lexema {lexeme} não faz parte da linguagem')
                exit()

            return tokens

        # Itera sobre o código aplicando a função tokens
        self.tabela = reduce(iconcat, map(tokens, code.split()))
        self.to_csv()
        return self.tabela

    # Escreve a tabela léxica num arquivo CSV
    def to_csv(self):
        def escape(str):
            return str if str not in [',', '"'] else '"'+str+'"'
        with open(self.folder+'/tabela_lexica.csv', 'w') as csv:
            for item in self.tabela:
                csv.write(f"{escape(item[0])},{escape(item[1])}\n")

    # Interface para o analisador sintático
    def gerador(self):
        for item in self.tabela:
            yield item[0]
        yield '$'

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("A execucao de make lexer run exige o parametro DIR=<diretorio>")
    analisador = AnalisadorLexico(sys.argv[1])

