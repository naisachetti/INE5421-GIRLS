from  enum import Enum
from Pilha import *

class TipoOp(Enum):
    FECHO = 1
    FECHO_POSITIVO = 2
    TALVEZ = 3
    CONCAT = 4
    OU = 5

class ArvoreSintatica:

    # Cria uma Arvore Sintatica para testes
    def __init__(self, regex: str) -> None:
        self.raiz = None
        self.simbolos: dict[int,Simbolo] = {} # Guarda cada nodo do tipo Simbolo por seu id, para busca rapida.
        self.cont_id = 1
        # Cria uma Arvore Sintatica para testes
        # self.criar_teste()
        # Cria a Arvore Sintatica para uma regex. regex deve ser recebido como argumento
        self.from_regex(regex)
        self.calcula_infos_nodos()

    # Retorna uma lista com os nomes dos simbolos, ou seja, o alfabeto contido na AS.
    def get_alfabeto(self):
        alfabeto: list[str] = []
        for simbolo in self.simbolos.values():
            if simbolo.get_nome() not in alfabeto and simbolo.get_nome() != '#' and simbolo.get_nome() != '&':
                alfabeto.append(simbolo.get_nome())
        return alfabeto

    # Retorna os estados do automato, com suas transições (inclui estado morto e transicoes para ele)
    def get_estados_automato(self):
        # Definicao do id de '#' em self.simbolos para a identificacao de estados finais
        id_simbolo_final = -1
        for id in self.simbolos.keys():
            if self.simbolos[id].get_nome() == '#':
                id_simbolo_final = id
                break

        estados = [] # Estados do automato, com suas transicoes
        alfabeto = self.get_alfabeto() # Alfabeto do automato

        # Criacao do estado morto
        morto: dict = {"nome": "Morto", "final": False}
        for simbolo in alfabeto:
            morto[simbolo] = [morto]
        estados.append(morto)

        # Algoritmo slide 45 de Analise Lexica
        # Criacao do estado inicial
        inicial: dict = {"nome": "q0", "final": (id_simbolo_final in self.raiz.get_firstpos())}
        pos_estados: dict[str, set] = {"q0":self.raiz.get_firstpos()} # Guarda ids dos simbolos da AS para cada estado
        estados.append(inicial)
        # Indicacao do estado inicial como nao marcado
        est_nao_marcados = [inicial]
        cont_estados = 0 # Contador utilizado na nomeacao dos estados
        # Criacao dos demais estados e suas transicoes
        while (len(est_nao_marcados) > 0):
            # print(estados)
            # print("\n")
            # Marca estado
            estado_origem = est_nao_marcados.pop(0)
            for simbolo in alfabeto:
                pos_simbolo = set() # Guarda ids dos simbolos da AS para um dos simbolos do estado marcado (estado_origem)

                # Faz a uniao dos followpos(id) para todo id do estado_origem que corresponde a simbolo
                for id in pos_estados[estado_origem["nome"]]:
                    if self.simbolos[id].get_nome() == simbolo:
                        pos_simbolo = pos_simbolo.union(self.simbolos[id].get_followpos())

                # Se pos_simbolo eh vazio, o estado_origem nao transita pelo simbolo
                if len(pos_simbolo) == 0:
                    estado_origem[simbolo] = [morto]
                # Caso contrario, transita
                else:
                    # Se estado eh novo
                    if pos_simbolo not in pos_estados.values():
                        # Cria novo estado
                        cont_estados += 1
                        novo_estado = {"nome": "q"+(str)(cont_estados), "final": (id_simbolo_final in pos_simbolo)}
                        pos_estados[novo_estado["nome"]] = pos_simbolo
                        estados.append(novo_estado)
                        # Indica estado como nao marcado
                        est_nao_marcados.append(novo_estado)
                        # Cria transicao do estado atual para o novo estado
                        estado_origem[simbolo] = [novo_estado]

                    # Se estado nao eh novo
                    else:
                        # Busca nome do estado de destino entre estados já registrados, a partir de pos_simbolo
                        nome_estado_dest = ""
                        for nome_estado in pos_estados.keys():
                            if pos_estados[nome_estado] == pos_simbolo:
                                nome_estado_dest = nome_estado

                        # Busca estado de destino entre estados já registrados, a partir do nome do estado
                        estado_dest = None
                        for estado in estados:
                            if estado["nome"] == nome_estado_dest:
                                estado_dest = estado
                        
                        # Cria transicao do estado de origem para o estado de destino
                        estado_origem[simbolo] = [estado_dest]
        
        return (estados, inicial)
    
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
            if isinstance(nodos.top(), Fecho) or isinstance(nodos.top(), FechoPositivo) or isinstance(nodos.top(), Talvez):
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
                arvore += nodos.top().get_nome()
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
            if len(nodo.get_firstpos()) > 0:
                for id in nodo.get_firstpos():
                    infos += (str)(id)+','
                infos = infos[:-1]
            infos += '}'

        if lastpos:
            infos += '{'
            if len(nodo.get_lastpos()) > 0:
                for id in nodo.get_lastpos():
                    infos += (str)(id)+','
                infos = infos[:-1]
            infos += '}'

        if followpos:
            if isinstance(nodo, Simbolo):
                infos += '{'
                if len(nodo.get_followpos()) > 0:
                    for id in nodo.get_followpos():
                        infos += (str)(id)+','
                    infos = infos[:-1]
                infos += '}'

        return infos

    # Cria uma AS a partir de uma regex prefixada
    def from_regex(self, regex: str):
        regex_processar = '.'+regex+'#'

        operadores = Pilha()

        is_literal = False
        for caracter in regex_processar:
            if caracter == '\\' and not is_literal:
                is_literal = True
            elif caracter == '*' and not is_literal:
                # print("Add *")
                nodo_pai = operadores.top()
                while (nodo_pai is not None) and (nodo_pai.cheio()):
                    operadores.pop()
                    nodo_pai = operadores.top()
                op = self.add_operador(TipoOp.FECHO, nodo_pai)
                operadores.push(op)
            elif caracter == '+' and not is_literal:
                # print("Add +")
                nodo_pai = operadores.top()
                while (nodo_pai is not None) and (nodo_pai.cheio()):
                    operadores.pop()
                    nodo_pai = operadores.top()
                op = self.add_operador(TipoOp.FECHO_POSITIVO, nodo_pai)
                operadores.push(op)            
            elif caracter == '?' and not is_literal:
                # print("Add ?")
                nodo_pai = operadores.top()
                while (nodo_pai is not None) and (nodo_pai.cheio()):
                    operadores.pop()
                    nodo_pai = operadores.top()
                op = self.add_operador(TipoOp.TALVEZ, nodo_pai)
                operadores.push(op)
            elif caracter == '.' and not is_literal:
                # print("Add .")
                nodo_pai = operadores.top()
                while (nodo_pai is not None) and (nodo_pai.cheio()):
                    operadores.pop()
                    nodo_pai = operadores.top()
                op = self.add_operador(TipoOp.CONCAT, nodo_pai)
                operadores.push(op)
            elif caracter == '|' and not is_literal:
                # print("Add |")
                nodo_pai = operadores.top()
                while (nodo_pai is not None) and (nodo_pai.cheio()):
                    operadores.pop()
                    nodo_pai = operadores.top()
                op = self.add_operador(TipoOp.OU, nodo_pai)
                operadores.push(op)
            else:
                # print("Add simbolo " + caracter)
                nodo_pai = operadores.top()
                while (nodo_pai is not None) and (nodo_pai.cheio()):
                    operadores.pop()
                    nodo_pai = operadores.top()
                self.add_simbolo(caracter, nodo_pai)
                is_literal = False

        self.simplificaOperadores()


    # Substitui nodos FechoPositivo e Talvez por nodos Fecho, Ou e Concat
    def simplificaOperadores(self):
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
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), FechoPositivo):
                if (filhos_visit.top() == 0):
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    nodos.push(nodos.top().get_filho())
                    filhos_visit.push(0)
                else:
                    fecho_pos = nodos.pop()
                    filhos_visit.pop()
                    
                    filho_fecho_pos = fecho_pos.get_filho()
                    novo_concat = Concat()
                    novo_concat.add_filho(filho_fecho_pos)
                    novo_fecho = self.add_operador(TipoOp.FECHO, novo_concat)
                    raiz_copia_subarvore = None
                    if isinstance(filho_fecho_pos, Simbolo):
                        raiz_copia_subarvore = filho_fecho_pos
                    else:
                        raiz_copia_subarvore = self.copiar_arvore(filho_fecho_pos)
                    novo_fecho.add_filho(raiz_copia_subarvore)
                    
                    nodo_pai = nodos.top()
                    if isinstance(nodo_pai, Fecho) or isinstance(nodo_pai, FechoPositivo) or isinstance(nodo_pai, Talvez):
                        nodo_pai.set_filho(novo_concat)
                    else:
                        if nodo_pai.get_filho_esq() == fecho_pos:
                            nodo_pai.set_filho_esq(novo_concat)
                        else:
                            nodo_pai.set_filho_dir(novo_concat)
            elif isinstance(nodos.top(), Talvez):
                if (filhos_visit.top() == 0):
                    num_visit = filhos_visit.pop()
                    filhos_visit.push(num_visit + 1)
                    nodos.push(nodos.top().get_filho())
                    filhos_visit.push(0)
                else:
                    talvez = nodos.pop()
                    filhos_visit.pop()
                    
                    filho_talvez = talvez.get_filho()
                    novo_ou = Ou()
                    self.add_simbolo('&', novo_ou)
                    novo_ou.add_filho(filho_talvez)
                    
                    nodo_pai = nodos.top()
                    if isinstance(nodo_pai, Fecho) or isinstance(nodo_pai, FechoPositivo) or isinstance(nodo_pai, Talvez):
                        nodo_pai.set_filho(novo_ou)
                    else:
                        if nodo_pai.get_filho_esq() == talvez:
                            nodo_pai.set_filho_esq(novo_ou)
                        else:
                            nodo_pai.set_filho_dir(novo_ou)
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
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), Simbolo):
                nodos.pop()
                filhos_visit.pop()

    # Dada uma raiz, faz uma copia da subarvore a partir dela.
    # Retorna a raiz da subarvore copiada.
    def copiar_arvore(self, raiz):
        nodos_original = Pilha()
        filhos_visit_originais = Pilha()
        nodos_copia = Pilha()

        copia_raiz = None
        if isinstance(raiz, Fecho):
            copia_raiz = Fecho()
        elif isinstance(raiz, FechoPositivo):
            copia_raiz = FechoPositivo()
        elif isinstance(raiz, Talvez):
            copia_raiz = Talvez()
        elif isinstance(raiz, Concat):
            copia_raiz = Concat()
        elif isinstance(raiz, Ou):
            copia_raiz = Ou()

        nodos_original.push(raiz)
        filhos_visit_originais.push(0)
        nodos_copia.push(copia_raiz)
        while (nodos_original.size() > 0):
            if isinstance(nodos_original.top(), Fecho) or isinstance(nodos_original.top(), FechoPositivo) or isinstance(nodos_original.top(), Talvez):
                if (filhos_visit_originais.top() == 0):
                    if isinstance(nodos_original.top().get_filho(), Simbolo):
                        self.add_simbolo(nodos_original.top().get_filho().get_nome(), nodos_copia.top())
                        num_visit = filhos_visit_originais.pop()
                        filhos_visit_originais.push(num_visit + 1)
                    else:
                        copia_filho = self.add_operador(self.recupera_tipo(nodos_original.top().get_filho()), nodos_copia.top())
                        nodos_copia.push(copia_filho)
                        num_visit = filhos_visit_originais.pop()
                        filhos_visit_originais.push(num_visit + 1)
                        nodos_original.push(nodos_original.top().get_filho())
                        filhos_visit_originais.push(0)
                else:
                    nodos_copia.pop()
                    nodos_original.pop()
                    filhos_visit_originais.pop()                    
            elif isinstance(nodos_original.top(), Concat) or isinstance(nodos_original.top(), Ou):
                if (filhos_visit_originais.top() == 0):
                    if isinstance(nodos_original.top().get_filho_esq(), Simbolo):
                        self.add_simbolo(nodos_original.top().get_filho_esq().get_nome(), nodos_copia.top())
                        num_visit = filhos_visit_originais.pop()
                        filhos_visit_originais.push(num_visit + 1)
                    else:
                        copia_filho = self.add_operador(self.recupera_tipo(nodos_original.top().get_filho_esq()), nodos_copia.top())
                        nodos_copia.push(copia_filho)
                        num_visit = filhos_visit_originais.pop()
                        filhos_visit_originais.push(num_visit + 1)
                        nodos_original.push(nodos_original.top().get_filho_esq())
                        filhos_visit_originais.push(0) 
                elif (filhos_visit_originais.top() == 1):
                    if isinstance(nodos_original.top().get_filho_dir(), Simbolo):
                        self.add_simbolo(nodos_original.top().get_filho_dir().get_nome(), nodos_copia.top())
                        num_visit = filhos_visit_originais.pop()
                        filhos_visit_originais.push(num_visit + 1)
                    else:
                        copia_filho = self.add_operador(self.recupera_tipo(nodos_original.top().get_filho_dir()), nodos_copia.top())
                        nodos_copia.push(copia_filho)
                        num_visit = filhos_visit_originais.pop()
                        filhos_visit_originais.push(num_visit + 1)
                        nodos_original.push(nodos_original.top().get_filho_dir())
                        filhos_visit_originais.push(0)
                else:
                    nodos_copia.pop()
                    nodos_original.pop()
                    filhos_visit_originais.pop() 

        return copia_raiz
                
    # Dado um nodo, analisa o tipo do objeto e retorna enumeracao equivalente
    def recupera_tipo(self, nodo):
        tipo = None
        if isinstance(nodo, Fecho):
            tipo = TipoOp.FECHO
        elif isinstance(nodo, FechoPositivo):
            tipo = TipoOp.FECHO_POSITIVO
        elif isinstance(nodo, Talvez):
            tipo = TipoOp.TALVEZ
        elif isinstance(nodo, Concat):
            tipo = TipoOp.CONCAT
        elif isinstance(nodo, Ou):
            tipo = TipoOp.OU

        return tipo

    # Adiciona um operador como filho de um determinado nodo da AS
    def add_operador(self, tipo: TipoOp, nodo_pai = None):
        if tipo == TipoOp.FECHO:
            op = Fecho()
        elif tipo == TipoOp.FECHO_POSITIVO:
            op = FechoPositivo()
        if tipo == TipoOp.TALVEZ:
            op = Talvez()
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
    def add_simbolo(self, nome: str, nodo_pai):
        simbolo = Simbolo(self.cont_id, nome)
        self.simbolos[self.cont_id] = simbolo
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
                    nodos.top().calcula_followpos(self.simbolos)
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
                        nodos.top().calcula_followpos(self.simbolos)
                    nodos.pop()
                    filhos_visit.pop()
            elif isinstance(nodos.top(), Simbolo):
                nodos.pop()
                filhos_visit.pop()

class Nodo:

    # Cria nodo da AS
    def __init__(self, anulavel = False, firstpos:set = set(), lastpos:set = set()):
        self.anulavel:bool = anulavel
        self.firstpos:set = firstpos
        self.lastpos:set = lastpos

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

    def get_tipo(self):
        return '*'

    def add_filho(self, novo_filho):
        if (self.filho is None):
            self.filho = novo_filho
        else:
            raise Exception("Impossivel adicionar filho. Nodo Fecho cheio. Possível causa: Regex mal formado.")
    
    def get_filho(self):
        return self.filho

    def set_filho(self, novo_filho):
        self.filho = novo_filho

    def cheio(self):
        return (self.filho is not None)
        
    def calcula_firstpos(self):
        fp1 = self.filho.get_firstpos()
        self.firstpos = fp1

    def calcula_lastpos(self):
        lp1 = self.filho.get_lastpos()
        self.lastpos = lp1

    def calcula_followpos(self, simbolos):
        for id in self.lastpos:
            simbolos[id].add_followpos(self.firstpos)

class FechoPositivo(Nodo):

    # Cria nodo do tipo Fecho (*) da AS
    def __init__(self):
        super().__init__(anulavel=True)
        self.filho = None

    def get_tipo(self):
        return '+'

    def add_filho(self, novo_filho):
        if (self.filho is None):
            self.filho = novo_filho
        else:
            raise Exception("Impossivel adicionar filho. Nodo Fecho cheio. Possível causa: Regex mal formado.")
    
    def get_filho(self):
        return self.filho

    def set_filho(self, novo_filho):
        self.filho = novo_filho

    def cheio(self):
        return (self.filho is not None)

class Talvez(Nodo):

    # Cria nodo do tipo Fecho (*) da AS
    def __init__(self):
        super().__init__(anulavel=True)
        self.filho = None

    def get_tipo(self):
        return '?'

    def add_filho(self, novo_filho):
        if (self.filho is None):
            self.filho = novo_filho
        else:
            raise Exception("Impossivel adicionar filho. Nodo Fecho cheio. Possível causa: Regex mal formado.")
    
    def get_filho(self):
        return self.filho
        
    def set_filho(self, novo_filho):
        self.filho = novo_filho

    def cheio(self):
        return (self.filho is not None)

class Concat(Nodo):

    # Cria nodo do tipo Concat (.) da AS
    def __init__(self):
        super().__init__(anulavel=False)
        self.filho_esq = None
        self.filho_dir = None

    def get_tipo(self):
        return '.'

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

    def set_filho_esq(self, novo_filho):
        self.filho_esq = novo_filho
    
    def set_filho_dir(self, novo_filho):
        self.filho_dir = novo_filho

    def cheio(self):
        return ((self.filho_esq is not None) and (self.filho_dir is not None))

    def calcula_anulavel(self):
        if self.filho_esq.is_anulavel() and self.filho_dir.is_anulavel():
            self.anulavel = True
        else:
            self.anulavel = False

    def calcula_firstpos(self):
        fp1 = self.filho_esq.get_firstpos()
        fp2 = self.filho_dir.get_firstpos()
        if self.filho_esq.is_anulavel():
            self.firstpos = fp1.union(fp2)
        else:
            self.firstpos = fp1

    def calcula_lastpos(self):
        lp1 = self.filho_esq.get_lastpos()
        lp2 = self.filho_dir.get_lastpos()
        if self.filho_dir.is_anulavel():
            self.lastpos = lp1.union(lp2)
        else:
            self.lastpos = lp2

    def calcula_followpos(self, simbolos):
        for id in self.filho_esq.get_lastpos():
            simbolos[id].add_followpos(self.filho_dir.get_firstpos())

class Ou(Nodo):

    # Cria nodo do tipo Ou (+) da AS
    def __init__(self):
        super().__init__(anulavel=False)
        self.filho_esq = None
        self.filho_dir = None

    def get_tipo(self):
        return '|'
    
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

    def set_filho_esq(self, novo_filho):
        self.filho_esq = novo_filho
    
    def set_filho_dir(self, novo_filho):
        self.filho_dir = novo_filho

    def cheio(self):
        return ((self.filho_esq is not None) and (self.filho_dir is not None))

    def calcula_anulavel(self):
        if self.filho_esq.is_anulavel() or self.filho_dir.is_anulavel():
            self.anulavel = True
        else:
            self.anulavel = False

    def calcula_firstpos(self):
        fp1 = self.filho_esq.get_firstpos()
        fp2 = self.filho_dir.get_firstpos()
        self.firstpos = fp1.union(fp2)

    def calcula_lastpos(self):
        lp1 = self.filho_esq.get_lastpos()
        lp2 = self.filho_dir.get_lastpos()
        self.lastpos = lp1.union(lp2)

class Simbolo(Nodo):

    # Cria nodo do tipo Simbolo da AS.
    #
    # Cada nodo fica guardado em um dicionario na classe ArvoreSintatica, para busca rápida.
    def __init__(self, id: int, nome:str):
        anulavel = (nome == '&')
        firstpos:set = set() if anulavel else {id}
        lastpos:set = set() if anulavel else {id}
        super().__init__(anulavel, firstpos, lastpos)
        self.id:int = id
        self.nome:str = nome
        self.followpos:set = set()

    def get_id(self):
        return self.id

    def get_nome(self):
        return self.nome

    def get_followpos(self):
        return self.followpos

    def add_followpos(self, novos_followpos:set):
        self.followpos = self.followpos.union(novos_followpos)