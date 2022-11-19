from  enum import Enum
from Pilha import *

class TipoOp(Enum):
    FECHO = 1
    CONCAT = 2
    OU = 3
    # TALVEZ = 4

class ArvoreSintatica:

    # Cria uma Arvore Sintatica para testes
    def __init__(self, regex: str) -> None:
        self.raiz = None
        self.simbolos = {} # Guarda o simbolo (caracter) para cada nodo do tipo Simbolo
        self.cont_id = 1
        # Cria uma Arvore Sintatica para testes
        # self.criar_teste()
        # Cria a Arvore Sintatica para uma regex. regex deve ser recebido como argumento
        self.from_regex(regex)

    # Função utilizada para verificação da integridade da AS.
    # Retorna o regex em notação prefixada da AS com informações sobre nodos anulaveis, 
    # seus firstpos, lastpos e/ou followpos.
    # Pode-se selecionar as informações desejadas mudando os parâmetros de controle para True.
    def get_arvore(self, anulaveis = False, firstpos = False, lastpos = False, followpos = False):
        nodos = Pilha()
        filhos_visit = Pilha()
        arvore = ""

        nodos.push(self.raiz)
        filhos_visit.push(0)
        while (nodos.size() > 0):
            if isinstance(nodos.top(), Fecho):
                if filhos_visit.top() == 0:
                    arvore += '(' + nodos.top().get_tipo()
                    arvore += self.infos_nodo(nodos.top(), anulaveis, firstpos, lastpos, followpos)
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    filhos_visit.push(0)
                    nodos.push(nodos.top().get_filho())
                else:
                    arvore += ')'
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), Concat) or isinstance(nodos.top(), Ou):
                if filhos_visit.top() == 0:
                    arvore += '(' + nodos.top().get_tipo()
                    arvore += self.infos_nodo(nodos.top(), anulaveis, firstpos, lastpos, followpos)
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    filhos_visit.push(0)
                    nodos.push(nodos.top().get_filho_esq())
                elif filhos_visit.top() == 1:
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    nodos.push(nodos.top().get_filho_dir())
                    filhos_visit.push(0)
                else:
                    arvore += ')'
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), Simbolo):
                arvore += self.simbolos[nodos.top().get_id()]
                arvore += self.infos_nodo(nodos.top(), anulaveis, firstpos, lastpos, followpos)
                nodos.pop()
                filhos_visit.pop()

        return arvore

    # Retorna uma string com informações sobre nodos anulaveis, seus firstpos, lastpos e/ou followpos.
    # Pode-se selecionar as informações desejadas mudando os parâmetros de controle para True.
    def infos_nodo(self, nodo, anulaveis = False, firstpos = False, lastpos = False, followpos = False):
        infos = ""
        if anulaveis:
            if nodo.is_anulavel():
                infos += "{n}"
        
        if firstpos:
            infos += '{'
            for id in nodo.get_firstpos():
                infos += (str)(id)
            infos += '}'

        if lastpos:
            infos += '{'
            for id in nodo.get_lastpos():
                infos += (str)(id)
            infos += '}'

        if followpos:
            if isinstance(nodo, Fecho) or isinstance(nodo, Concat):
                infos += '{'
                for id in nodo.get_followpos():
                    infos += (str)(id)
                infos += '}'

        return infos

    # Cria uma AS de teste para (.(.(.(.(*(+ab))a)b)b)#)
    def criar_teste(self):
        operadores = Pilha()

        op = self.add_operador(TipoOp.CONCAT)
        operadores.push(op)
        op = self.add_operador(TipoOp.CONCAT, operadores.top())
        operadores.push(op)
        op = self.add_operador(TipoOp.CONCAT, operadores.top())
        operadores.push(op)
        op = self.add_operador(TipoOp.CONCAT, operadores.top())
        operadores.push(op)
        op = self.add_operador(TipoOp.FECHO, operadores.top())
        operadores.push(op)
        op = self.add_operador(TipoOp.OU, operadores.top())
        operadores.push(op)
        self.add_simbolo('a', operadores.top())
        self.add_simbolo('b', operadores.top())
        operadores.pop()
        operadores.pop()
        self.add_simbolo('a', operadores.top())
        operadores.pop()
        self.add_simbolo('b', operadores.top())
        operadores.pop()
        self.add_simbolo('b', operadores.top())
        operadores.pop()
        self.add_simbolo('#', operadores.top())
        operadores.pop()

    # Cria uma AS a partir de uma regex
    def from_regex(self, regex: str):
        regex_processar = '(.'+regex+'#)'
        operadores = Pilha()

        for caracter in regex_processar:
            # print(caracter)
            if caracter == '(' or caracter == ' ':
                pass
            elif caracter == ')':
                # print("Pop")
                operadores.pop()
            elif caracter == '*':
                # print("Add *")
                op = self.add_operador(TipoOp.FECHO, operadores.top())
                operadores.push(op)
            elif caracter == '.':
                # print("Add .")
                op = self.add_operador(TipoOp.CONCAT, operadores.top())
                operadores.push(op)
            elif caracter == '+':
                # print("Add +")
                op = self.add_operador(TipoOp.OU, operadores.top())
                operadores.push(op)
            else:
                # print("Add simbolo")
                self.add_simbolo(caracter, operadores.top())

    # Adiciona um operador como filho de um determinado nodo da AS
    def add_operador(self, tipo: TipoOp, nodo_pai = None):
        if tipo == TipoOp.FECHO:
            op = Fecho()
        elif tipo == TipoOp.CONCAT:
            op = Concat()
        elif tipo == TipoOp.OU:
            op = Ou()

        if self.raiz is None:
            self.raiz = op
        else:
            if nodo_pai is None:
                raise Exception("Impossivel adicionar operador. Não há operador pai e raiz esta ocupada.")
            nodo_pai.add_filho(op)

        return op

    # Adiciona um simbolo como filho de um determinado nodo da AS
    def add_simbolo(self, caracter: chr, nodo_pai):
        if (caracter == '&'):
            simbolo = Simbolo(self.cont_id, anulavel=True)
        else:
            simbolo = Simbolo(self.cont_id)
        self.simbolos[self.cont_id] = caracter
        self.cont_id += 1
        nodo_pai.add_filho(simbolo)

    # Faz o calculo para definir nodos anulaveis, firstpos, lastpos e followpos da AS
    def calcula_infos_nodos(self):
        nodos = Pilha()
        filhos_visit = Pilha()

        nodos.push(self.raiz)
        filhos_visit.push(0)
        while (nodos.size() > 0):
            if isinstance(nodos.top(), Fecho):
                if (filhos_visit.top() == 0):
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    nodos.push(nodos.top().get_filho())
                    filhos_visit.push(0)
                else:
                    nodos.top().calcula_firstpos()
                    nodos.top().calcula_lastpos()
                    nodos.top().calcula_followpos()
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), Concat) or isinstance(nodos.top(), Ou):
                if (filhos_visit.top() == 0):
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    nodos.push(nodos.top().get_filho_esq())
                    filhos_visit.push(0)
                elif (filhos_visit.top() == 1):
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    nodos.push(nodos.top().get_filho_dir())
                    filhos_visit.push(0)
                else:
                    nodos.top().calcula_anulavel()
                    nodos.top().calcula_firstpos()
                    nodos.top().calcula_lastpos()
                    if isinstance(nodos.top(), Concat):
                        nodos.top().calcula_followpos()
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), Simbolo):
                nodos.pop()
                filhos_visit.pop()

class Nodo:

    # Cria nodo da AS
    def __init__(self, anulavel = False, firstpos = [], lastpos = []):
        self.anulavel = anulavel
        self.firstpos = firstpos
        self.lastpos = lastpos

    def is_anulavel(self):
        return self.anulavel

    def get_firstpos(self):
        return self.firstpos
    
    def get_lastpos(self):
        return self.lastpos

class Fecho(Nodo):

    # Cria nodo do tipo Fecho (*) da AS
    def __init__(self):
        super().__init__(anulavel=True)
        self.filho = None
        self.followpos = []

    def get_tipo(self):
        return '*'

    def get_followpos(self):
        return self.followpos

    def add_filho(self, novo_filho):
        if (self.filho is None):
            self.filho = novo_filho
        else:
            raise Exception("Impossivel adicionar filho. Nodo Fecho cheio. Possível causa: Regex mal formado.")
    
    def get_filho(self):
        return self.filho
        
    def calcula_firstpos(self):
        pass

    def calcula_lastpos(self):
        pass

    def calcula_followpos(self):
        pass

class Concat(Nodo):

    # Cria nodo do tipo Concat (.) da AS
    def __init__(self):
        super().__init__(anulavel=False)
        self.filho_esq = None
        self.filho_dir = None
        self.followpos = []

    def get_tipo(self):
        return '.'

    def get_followpos(self):
        return self.followpos

    def add_filho(self, novo_filho):
        if (self.filho_esq is None):
            self.filho_esq = novo_filho
        elif (self.filho_dir is None):
            self.filho_dir = novo_filho
        else:
            raise Exception("Impossivel adicionar filho. Nodo Concat cheio. Possível causa: Regex mal formado.")

    def get_filho_esq(self):
        return self.filho_esq

    def get_filho_dir(self):
        return self.filho_dir

    def calcula_anulavel(self):
        if self.filho_esq.is_anulavel() and self.filho_dir.is_anulavel():
            self.anulavel = True
        else:
            self.anulavel = False

    def calcula_firstpos(self):
        pass

    def calcula_lastpos(self):
        pass

    def calcula_followpos(self):
        pass

class Ou(Nodo):

    # Cria nodo do tipo Ou (+) da AS
    def __init__(self):
        super().__init__(anulavel=False)
        self.filho_esq = None
        self.filho_dir = None

    def get_tipo(self):
        return '+'

    def add_filho(self, novo_filho):
        if (self.filho_esq is None):
            self.filho_esq = novo_filho
        elif (self.filho_dir is None):
            self.filho_dir = novo_filho
        else:
            raise Exception("Impossivel adicionar filho. Nodo Ou cheio. Possível causa: Regex mal formado.")

    def get_filho_esq(self):
        return self.filho_esq

    def get_filho_dir(self):
        return self.filho_dir

    def calcula_anulavel(self):
        if self.filho_esq.is_anulavel() or self.filho_dir.is_anulavel():
            self.anulavel = True
        else:
            self.anulavel = False

    def calcula_firstpos(self):
        pass

    def calcula_lastpos(self):
        pass

class Simbolo(Nodo):

    # Cria nodo do tipo Simbolo da AS.
    #
    # O simbolo (caracter) representado por cada nodo fica guardado 
    # em um dicionario na classe ArvoreSintatica, para busca rápida.
    def __init__(self, id: int, anulavel = False):
        firstpos = [] if anulavel else [id]
        lastpos = [] if anulavel else [id]
        super().__init__(anulavel, firstpos, lastpos)
        self.id = id

    def get_id(self):
        return self.id