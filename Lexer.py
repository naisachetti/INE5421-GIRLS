from Automato import *
from regex_lib import read_regex

from functools import reduce
from operator import iconcat
import sys

class AnalisadorLexico:
    def __init__(self, folder, nome_programa=""):
        self.folder = folder
        self.automato = None
        self.tabela_lexica = []
        self.tabela_simbolos = {}
        self.nome_programa = nome_programa
        self.from_file()
        self.analisar()
        self.to_csv()

    # Pega o arquivo 'tokens' e monta o automâto que reconhece a linguagem a partir das definições no arquivo
    def from_file(self):
        tokens_path = self.folder + '/tokens'

        # Le o arquivo de definições regulares e tokens
        tokens_regex = read_regex(tokens_path)
        # Cria os autômatos a partir das regex
        autos = [Automato().from_regex(tokens_regex[token], token) for token in tokens_regex.keys()]
        # Faz a união dos automâtos
        self.automato = reduce(Automato.uniao_com, autos)
        # Escreve o automâto em um arquivo
        self.automato.to_file(self.folder + '/automata')

    # Analisa o arquivo 'program'
    def analisar(self):
        source = ""
        if self.nome_programa != "":
            source = self.folder+'/'+self.nome_programa
        else:
            source = self.folder + '/program'

        with open(source, 'r') as file:
            code = file.read()

        # Substitui caracteres especiais por espaços
        for char in ['\t', '\r']:
            code = code.replace(char, '')
        code = code.split('\n')

        # Obtem todos os tokens de uma string
        def tokens(word):
            tokens = []
            begin = 0
            forward = 0
            max_forward = 10
            try:
                while 1:
                    token = ''
                    begin = forward
                    forward = begin + 1

                    lexeme = word[begin:forward]
                    if lexeme == ' ': continue
                    if lexeme == '': break
                    if lexeme == '"':
                        forward = word[begin+1:].find('"') + begin + 2
                        lexeme = word[begin:word[begin+1:].find('"')]
                        token = 'string_constant'
                    elif lexeme == '~':
                        forward = word[begin+1:].find('~') + begin + 2
                        lexeme = word[begin:forward]
                        token = 'comment'
                    else:
                        next = [word[begin:forward+i+1] for i in range(max_forward) if not ' ' in word[begin:forward+i+1]]

                        # Enquanto (não reconhecer o lexema ou reconhecer o lexema adicionado de um caractere)
                        # e não passamos do fim da palavra
                        while (not self.automato.reconhece(lexeme) or any(map(self.automato.reconhece, next))) \
                                and forward <= len(word):

                            forward += 1
                            lexeme = word[begin:forward]
                            next.pop(0)
                            if not ' ' in word[begin:forward+max_forward]:
                                next.append(word[begin:forward+max_forward])
                        token = self.automato.token(lexeme)

                    print((token, lexeme))
                    tokens.append((token, lexeme))
                    # print(f'{token:>10} {lexeme}')

            # Caso o automâto não tenha uma transição, o lexema não faz parte da linguagem
            except KeyError:
                print(f'Lexema "{lexeme}" não faz parte da linguagem')
                exit()

            return tokens

        # Itera sobre o código aplicando a função tokens
        for index, line in enumerate(code):
            aux = tokens(line)
            self.tabela_lexica += aux
            for t in filter(lambda x: x[0] == 'ident', aux):
                if t[1] in self.tabela_simbolos:
                    self.tabela_simbolos[t[1]].append(index)
                else:
                    self.tabela_simbolos[t[1]] = [index]

        self.tabela_lexica.append(('$', '$'))

    # Escreve a tabela léxica num arquivo CSV
    def to_csv(self):
        def escape(str):
            return str if (',' not in str and '"' not in str) else '"'+str+'"'
        def list_to_text(l):
            return str(l)[1:-1]

        with open(self.folder+'/tabela_lexica.csv', 'w') as csv:
            for item in self.tabela_lexica:
                csv.write(f"{escape(item[0])},{escape(item[1])}\n")
        with open(self.folder+'/tabela_simbolos.csv', 'w') as csv:
            for item in self.tabela_simbolos.items():
                a = escape(list_to_text(item[1]))
                csv.write(f"{escape(item[0])},{a}\n")

    # Interface para o analisador sintático
    def gerador(self):
        tabela = list(filter(lambda item: item[0] != 'comment', self.tabela_lexica))
        for item in tabela:
            yield item

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("A execucao de make lexer run exige os parametros DIR=<diretorio> PROGRAM=<programa>")
    else:
        analisador = AnalisadorLexico(sys.argv[1], sys.argv[2])
        print("Arquivos tabela_lexica.csv e tabela_simbolos.csv criadas no diretorio")
