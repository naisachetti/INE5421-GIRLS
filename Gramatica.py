from random import randrange
from string import ascii_uppercase

class Production(str):
    def __init__(self, conteudo: str, separation_par = "space", nt_identification = None):
        self.conteudo = conteudo.split()
        self.separation_par = separation_par #char ou space
        self.nt_identification = nt_identification #caracteres especiais no inicio e fim de nao terminais
        self.len = 0
        
        self.iterator = None
        if self.separation_par == "space":
            self.len =  len(self.conteudo)

        elif self.nt_identification is None:
            self.len = len(self.conteudo)
        else:
            # Quando os nao terminais tem identificadores mas nao espaco eh um saco de tratar
            
            # Esse techo separa os nt terminais do resto, que fica agrupado
            nt_separados = []
            start = 0
            for i, caracter in enumerate(self.conteudo):
                if caracter == self.nt_identification[0] and i:
                    nt_separados.append(self.conteudo[start:i])
                    start = i
                if caracter == self.nt_identification[1]:
                    nt_separados.append(self.conteudo[start:i+1])
                    start = i+1
            else:
                if nt_separados[-1][-1] != self.conteudo[-1]:
                    nt_separados.append(self.conteudo[start:])
            
            # Esse trecho separa os terminais aglutinados
            tudo_separado = []
            for grupo in nt_separados:
                if self.nt_identification[0] in grupo or self.nt_identification[1] in grupo:
                    tudo_separado.append(grupo)
                else:
                    for letter in grupo:
                        tudo_separado.append(letter)
            
            # Retorna o iterador tratado
            self.len = len(tudo_separado)

    def __len__(self):
        return self.len

    def copy(self):
        copia = Production(" ".join(self.conteudo), self.separation_par, self.nt_identification)
        return copia
    
    def __iter__(self):
        # return self.iterator
        if self.separation_par == "space":
            return iter(self.conteudo)
        elif self.nt_identification is None:
            return iter(self.conteudo)
        else:
            # Quando os nao terminais tem identificadores mas nao espaco eh um saco de tratar
            
            # Esse techo separa os nt terminais do resto, que fica agrupado
            nt_separados = []
            start = 0
            for i, caracter in enumerate(self.conteudo):
                if caracter == self.nt_identification[0] and i:
                    nt_separados.append(self.conteudo[start:i])
                    start = i
                if caracter == self.nt_identification[1]:
                    nt_separados.append(self.conteudo[start:i+1])
                    start = i+1
            else:
                if nt_separados[-1][-1] != self.conteudo[-1]:
                    nt_separados.append(self.conteudo[start:])
            
            # Esse trecho separa os terminais aglutinados
            tudo_separado = []
            for grupo in nt_separados:
                if self.nt_identification[0] in grupo or self.nt_identification[1] in grupo:
                    tudo_separado.append(grupo)
                else:
                    for letter in grupo:
                        tudo_separado.append(letter)
            
            # Retorna o iterador tratado
            return iter(tudo_separado)

    def first(self):
        return self[0]

    def __getitem__(self, __i) -> str:
        return self.conteudo[__i]

    def __list__(self):
        return self.conteudo

    def __repr__(self) -> str:
        return " ".join(self.conteudo)
    
    def index(self, valor) -> int:
        # print(self.conteudo, valor)
        return self.conteudo.index(valor)

class Gramatica:

    def __init__(self) -> None:
        
        # Cria uma gramatica vazia
        self.inicial = None
        self.terminais = []
        self.nao_terminais = []

        # As producoes sao dicionarios provavelmente ainda n pensei 100% nisso
        self.producoes = {}
        self.nt_identification = None #Caracteres que identificam nao terminais. Ex: <NT> esse atributo seria "<>"

    # Representacao da gramatica pra prints
    def __repr__(self) -> str:
        saida = ""
        for nao_terminal, producoes in self.producoes.items():
            producoes = " | ".join(producoes)
            saida += f"{nao_terminal} ::= {producoes}\n"
        return saida[:-1]

    # Retorna uma copia da gramatica
    def copy(self):
        copia = Gramatica()
        copia.inicial = self.inicial
        copia.terminais = self.terminais.copy()
        copia.nao_terminais = self.nao_terminais.copy()
        copia.producoes = self.producoes.copy()
        return copia

    # Le a gramatica de um arquivo
    def from_file(self, filename: str):
        with open(filename, "r") as arquivo:
            conjunto_simbolos = set()
            for linha in arquivo:
                if linha.strip() == "":
                    continue
                nao_terminal, producoes = [palavra.strip() for palavra in linha.split("::=")]
                
                # Simbolo inicial da gramatica
                if self.inicial == None:
                    self.inicial = nao_terminal
                
                # Adiciona nao terminal na lista
                if not nao_terminal in self.nao_terminais: self.nao_terminais.append(nao_terminal)
                
                # TODO: TEM QUE RECEBER O PADRAO DE PRODUCAO DE ALGUM LUGAR PRA SABER ITERAR SOBRE
                producoes = [Production(palavra.strip()) for palavra in producoes.split("|")]
                
                # Criacao dos dicionarios
                self.producoes[nao_terminal] = producoes

                # Leitura de todos os simbolos novos
                for producao in producoes:
                    for simbolo in producao:
                        
                        # Assume que nao terminais sao um unico caracter identificado por ser letra maiuscula
                        if self.nt_identification is None:
                            conjunto_simbolos.add(simbolo) 
                        else:
                            if self.nt_identification[0] in simbolo:
                                if not simbolo in self.nao_terminais: self.nao_terminais.append(simbolo)
                            else:
                                if not simbolo in self.terminais: self.terminais.append(simbolo)
            for simbolo in conjunto_simbolos.copy():
                if simbolo in self.nao_terminais:
                    conjunto_simbolos.remove(simbolo)
                self.terminais = list(conjunto_simbolos)               
        return self

    # Escreve a gramatica num arquivo
    def to_file(self, filename: str):
        with open(filename, "w") as arquivo:
            for nao_terminal, producoes in self.producoes.items():
                producoes = " | ".join(producoes)
                arquivo.write(f"{nao_terminal} -> {producoes}")

    # Retorna um novo nao terminal 
    def novo_nao_terminal(self, original = None):
        if original:
            return original + "'"
        
        alfabeto = list(ascii_uppercase)
        sufix = 0
        if self.nt_identification is None:
            for _ in range(10000):
            # Tenta retornar uma letra do alfabeto
                for letra in alfabeto:
                    proposta = letra+"".join(["'" for _ in range(sufix)])
                    if not proposta in self.nao_terminais:
                        self.nao_terminais.append(letra)
                        return letra
                else:
                    sufix += 1
            else: 
                raise RuntimeError("Nao consegui gerar um nome novo")

    # Simplesmente retorna uma producao aleatoria dentre as possiveis
    def random_production(self, nao_terminal: str) -> str:
        producao = self.producoes[nao_terminal][randrange(len(self.producoes[nao_terminal]))]
        if producao == "&":
            return ""
        else:
            return producao

    # Gera uma palavra aleatoria da gramatica
    def generate_word(self, limit: int = 100):
        forma_sentencial = Production(self.inicial)

        # Ao inves de um while eh um for com limite de 100 iteracoes pra n ir pra sempre
        for _ in range(limit):
            # print("forma:", repr(forma_sentencial))
            for simbolo in forma_sentencial:
                if simbolo in self.nao_terminais:
                    # print(forma_sentencial)
                    indice = forma_sentencial.index(simbolo)
                    nova_prod = self.random_production(simbolo)
                    # print(f"{simbolo}({indice}): {nova_prod}")
                    forma_sentencial = Production(" ".join(forma_sentencial[:indice])+" "+nova_prod+" "+" ".join(forma_sentencial[indice+1:]))
                    break
            else:
                break
        else:
            return None
        return Production(" ".join(forma_sentencial)+" $")

    # Marca simbolos alcancaveis
    def alcance(self, nao_terminal):
        for producao in self.producoes[nao_terminal]:
            for simbolo in producao:
                if simbolo in self.nao_terminais:
                    if not self.alcancavel[simbolo]:
                        self.alcancavel[simbolo] = True
                        self.alcance(simbolo)

    # Elimina simbolos inalcancaveis
    def sem_inalcancaveis(self):
        copia = self.copy()
        copia.alcancavel = {nt: False for nt in copia.nao_terminais}
        copia.alcancavel[copia.inicial] = True
        copia.alcance(copia.inicial)
        for nt in copia.alcancavel:
            if not copia.alcancavel[nt]:
                copia.nao_terminais.remove(nt)
                copia.producoes.pop(nt)
        return copia

    # Altera a gramatica alterando as producoes da cabeca pra que "incorporem" as producoes do corpo e o eliminem
    def herdar_producoes(self, nt_cabeca: str, nt_corpo: str):
        # print(nt_cabeca, nt_corpo)
        novas_producoes = []

        # Itera sobre cada producao
        for producao in self.producoes[nt_cabeca]:
            destruir = 0

            # Atavessa os simbolos da producao
            for index, simbolo in enumerate(producao):
                
                # Simbolo analisado eh o que vai ser substituido por suas producoes
                if simbolo == nt_corpo:
                    destruir += 1
                    if destruir > 1:
                        break #TODO: ISSO EH GAMBIARRA
                        raise RuntimeError(f"POISE O SIMBOLO PRA HERDAR {nt_corpo} APARECEU 2 VEZES EM {producao}")
                    for herdada in self.producoes[nt_corpo]:
                        if herdada == "&":
                            if len(producao) > 1:
                                novas_producoes.append(Production(" ".join(producao[:index])+" "+" ".join(producao[index+1:])))
                            else:
                                novas_producoes.append(Production("&"))
                        else:
                            novas_producoes.append(Production(" ".join(producao[:index])+" "+herdada+" "+" ".join(producao[index+1:])))
            if destruir == 1:
                self.producoes[nt_cabeca].remove(producao)
        # self.producoes[nt_cabeca] += novas_producoes
        for producao in novas_producoes:
            if not producao in self.producoes[nt_cabeca]:
                # print(producao, self.producoes[nt_cabeca])
                self.producoes[nt_cabeca].append(producao)

     # Retorna a gramatica sem producoes unitarias
    def sem_unitarias(self):
        copia = self.copy()
        for nao_terminal, producoes in copia.producoes.items():
            houve_alteracao = True
            while houve_alteracao:
                houve_alteracao = False
                for producao in producoes:
                    if len(producao) == 1 and producao[0] in copia.nao_terminais:
                        copia.herdar_producoes(nao_terminal, producao[0])
                        houve_alteracao = True
        return copia

    # Encontra nao terminais anulaveis
    def anulaveis(self):
        # Encontra os simbolos anulaveis
        anulaveis = ["&"]
        alterado_flag = True
        while alterado_flag:
            # Flag pra ver se algum nao terminal passou a ser anulavel nessa iteracao
            alterado_flag = False
            for nao_terminal, producoes in self.producoes.items():
                
                if nao_terminal in anulaveis:
                    continue
                
                for producao in producoes:
                    for simbolo in producao:
                        # Se um simbolo ja nao for anulavel a producao como um todo nao eh
                        if not simbolo in anulaveis:
                            break
                    else:
                        # Todos simbolos anulaveis
                        alterado_flag = True
                        anulaveis.append(nao_terminal)
                        # Nao ha mais por que analisar as producoes deste simbolo
                        break
        return anulaveis
    
    # Retorna a gramatica sem epslon producoes
    def e_livre(self):
        copia: Gramatica = self.copy()

        # Encontra os simbolos anulaveis
        anulaveis = copia.anulaveis()
        
        # Novo estado inicial caso necessario
        if copia.inicial in anulaveis:
            novo_inicial = copia.novo_nao_terminal()
            copia.producoes[novo_inicial] = [Production(copia.inicial), Production("&")]
            copia.inicial = novo_inicial
        
        # Elimina as & producoes
        for nao_terminal, producoes in copia.producoes.items():
            if nao_terminal == copia.inicial:
                continue
            if "&" in producoes:
                producoes.remove("&")

        # Gera as producoes livres
        for nao_terminal, producoes in copia.producoes.items():
            for producao in producoes:
                # print(nao_terminal, producoes)
                if len(producao) == 1:
                    continue
                for index, simbolo in enumerate(producao):
                    # print(index, simbolo)
                    if simbolo in anulaveis:
                        # print(simbolo, "lista",list(producao), producao[index+1:])
                        nova_prod = Production(" ".join(producao[:index])+" "+" ".join(producao[index+1:]))
                        # print(nova_prod)
                        if not nova_prod in producoes:
                            producoes.append(nova_prod)
        return copia

    # Retorna a gramatica sem loops
    #TODO: tem loops nao diretos, procurar eles
    def sem_loop(self):
        copia = self.copy()
        for nt, producoes in copia.producoes.items():
            if nt in producoes:
                producoes.remove(nt)
        return copia

    # Altera a gramatica para retirar recursao direta daquele nao terminal
    def eliminar_recursao_direta(self, nao_terminal: str):
        
       # Separa producoes recursivas de nao recursivas
        producoes_recursivas = []
        producoes_nao_recursivas = []
        for producao in self.producoes[nao_terminal]:
            if nao_terminal != producao[0]:
                producoes_nao_recursivas.append(producao)
            if nao_terminal == producao[0]:
                producoes_recursivas.append(producao)

        # Se nao ha producoes recursivas nao ha o que fazer
        if len(producoes_recursivas) == 0:
            return

        # Eliminacao de recursoes diretas
        novo_simbolo = self.novo_nao_terminal(nao_terminal)
        self.producoes[novo_simbolo] = [Production("&")]

        self.producoes[nao_terminal] = [Production(producao+" "+novo_simbolo) for producao in producoes_nao_recursivas]
        self.producoes[novo_simbolo] += [Production(" ".join(producao[1:])+" "+novo_simbolo) for producao in producoes_recursivas]

    # Retorna a gramatica sem recursao a esquerda
    def sem_recursao(self):
        copia = self.copy()#.sem_loop().e_livre()
        # print(copia)

        # Notacao dos slides da professora
        for i, ai in enumerate(copia.nao_terminais):
            
            # Eliminacao da recursao indireta
            for _, aj in zip(range(i), copia.nao_terminais):
                for pi in copia.producoes[ai]:
                    if pi[0] == aj:
                        for pj in copia.producoes[aj]:
                            # print(type(pi[1:]), type(pj))
                            copia.producoes[ai].append(Production(pj+" "+" ".join(pi[1:])))
                        copia.producoes[ai].remove(pi)

            # Eliminacao da recursao direta
            copia.eliminar_recursao_direta(ai)

        return copia

    # Altera a gramatica para retirar nao determinismo direto
    def eliminar_nd_direto(self, nao_terminal: str):
        houve_alteracao = True
        novo_nt = None
        while houve_alteracao:

            houve_alteracao = False
            simbolos_iniciais = [producao[0] for producao in self.producoes[nao_terminal]]
            for simbolo in simbolos_iniciais:
                # ha nao determinismo com este simbolo
                if simbolos_iniciais.count(simbolo) > 1:
                    houve_alteracao = True
                    # Separa os indices das producoes que sao repetidas (sim esse codigo ta horrivel)
                    indices = [index for index, simbolo_repetido in enumerate(simbolos_iniciais) if simbolo == simbolo_repetido]

                    # Cria um novo nao terminal que produz dos nao deterministicos
                    novo_nt = self.novo_nao_terminal()
                    self.producoes[novo_nt] = [Production(" ".join(producao[1:])) for producao in self.producoes[nao_terminal] if self.producoes[nao_terminal].index(producao) in indices]
                    for producao in self.producoes[novo_nt]:
                        if producao == "":
                            self.producoes[novo_nt].remove("")
                            self.producoes[novo_nt].append(Production("&"))

                    # Elimina as producoes nao deterministicas
                    for offset, indice in enumerate(indices):
                        self.producoes[nao_terminal].pop(indice-offset)

                    # Transicao que leva pro novo nao terminal
                    self.producoes[nao_terminal].append(Production(simbolo+" "+novo_nt))

                    break
        
        return novo_nt # Retorna o novo terminal criado

    # OBSOLETO POSSIVELMENTE
    # Recebe uma lista de simbolos iniciais, e retorna uma dos iniciais alcancaveis dando um passo a mais nos NT
    def inicias_proximo_passo(self, alcancaveis: dict):
        # alcancaveis = {"inferteis": [], "ferteis": []}
        novos_alcancaveis = []
        for simbolo in alcancaveis["ferteis"]:
            # Nao terminais nao importam
            if simbolo in self.terminais + ["&"]:
                continue

            # Todos os primeiros simbolos alcancaveis por este nao terminal
            novos_alcancaveis += [producao[0] for producao in self.producoes[simbolo]]

        alcancaveis["inferteis"] += alcancaveis["ferteis"]
        alcancaveis["ferteis"] = novos_alcancaveis
        ha_duplicatas = len(alcancaveis["inferteis"]) - len(set(alcancaveis["inferteis"])) > 0
        return alcancaveis, ha_duplicatas
            
    # Retorna a gramatica fatorada
    # ALTERA A GRAMATICA DE VDD
    def fatorada(self):
        copia = self.copy()
        # Elimina ND direto iniciais
        for nao_terminal in copia.nao_terminais:
            copia.eliminar_nd_direto(nao_terminal)
        
        # TODO: POSSIVEL PROBLEMA PRA GRAMATICAS COMPLEXAS
        # Se ha nao terminal a esquerda entao ta na hora de herdar producao
        nt_lista = list(copia.producoes.keys())
        for nao_terminal in nt_lista:
            # copia.eliminar_nd_direto(nao_terminal)
            # Limite de 1000 derivacoes sucessivas
            for _ in range(100):
                if len(copia.producoes[nao_terminal]) > 20:
                    print(copia)
                    raise RuntimeError("Nao consegui fatorar a gramatica (muita producao)")
                for producao in copia.producoes[nao_terminal]:
                    # if nao_terminal == "F":
                    #     print("producao", producao)
                    #     print("producoes", copia.producoes[nao_terminal])
                    # Comeca de fato com um nao terminal
                    print(nao_terminal, copia.producoes[nao_terminal], producao)
                    if producao[0] in copia.nao_terminais:
                        # print(nao_terminal, producao[0], list(producao))
                        copia.herdar_producoes(nao_terminal, producao[0])
                        
                        break
                else:
                    # Se ele nao conseguiu herdar nada
                    break
                # copia.eliminar_nd_direto(nao_terminal)
            else:
                raise RuntimeError("Nao consegui fatorar a gramatica (limite de derivacoes)")
            novo_nt = copia.eliminar_nd_direto(nao_terminal)
            if novo_nt:
                nt_lista.append(novo_nt)
        
        return copia

    # Retorna o firstpos de uma producao
    def first_prod(self, producao: Production):
        if producao[0] in self.terminais or producao[0] == "&":
            return {producao[0]}
        first = set()
        for simbolo in producao:
            first = first.union(self.__firstpos_nt(simbolo))
            if not simbolo in self.anulaveis():
                break
        return first
    
    # Calcula o firstpos de um nao terminal
    def __firstpos_nt(self, nt: str):
        first = set()
        for producao in self.producoes[nt]:
            firspos_producao = producao.first()
            if firspos_producao in self.terminais or firspos_producao == "&":
                first.add(firspos_producao)
            # Firspos eh um NT
            else:
                for simbolo in producao:
                    # Adiciona nao terminal no firstpos e sai
                    if simbolo in self.terminais:
                        first.add(simbolo)
                        break

                    # Acrescenta o firstpos do nao terminal e continua se for anulavel
                    elif simbolo in self.nao_terminais:
                        first = first.union(self.__firstpos_nt(simbolo))
                        if not simbolo in self.anulaveis():
                            break
                        
        if nt in self.anulaveis():
            first.add("&")
        return first

    # Calcula o firstpos da gramatica
    def firspost(self):
        first = {nt:[] for nt in self.nao_terminais}
        for nt in self.nao_terminais:
            first[nt] = self.__firstpos_nt(nt)
        return first

    # Calcula o followpos de um nao terminal
    def __followpos_nt(self, nt: str, analisys_set = None):
        if analisys_set is None:
            analisys_set = set()
        analisys_set.add(nt)
        # print(analisys_set)
        follow = set()
        # Fim de arquivo sempre ao fim do simbolo inicial
        if nt is self.inicial:
            follow.add("$")
        for nt_analisado, producoes in self.producoes.items():
            for producao in producoes:
                for i, simbolo in enumerate(producao):
                    if nt == simbolo:
                        # Ultimo simbolo da producao
                        if i == len(producao) - 1:
                            if not nt_analisado in analisys_set:
                                follow = follow.union(self.__followpos_nt(nt_analisado, analisys_set.copy()))
                        else:
                            prox = producao[i+1]
                            # Proximo simbolo eh um terminal
                            if prox in self.terminais:
                                follow.add(prox)
                            # Proximo simbolo eh um nao terminal
                            else:
                                # Tem que ver todos os proximos e ver se eles sao anulaveis
                                for j in range(i+1, len(producao)):
                                    if producao[j] != nt:
                                        follow = follow.union(self.__firstpos_nt(producao[j]))
                                    if "&" in follow:
                                        follow.remove("&")
                                    if not producao[j] in self.anulaveis():
                                        break
                                else:
                                    if not producao[j] in analisys_set:
                                        analisys_set.add(producao[j])
                                        follow = follow.union(self.__followpos_nt(nt_analisado, analisys_set.copy()))
        return follow
    
    # Calcula o firstpos da gramatica
    def followpost(self):
        follow = {nt:[] for nt in self.nao_terminais}
        for nt in self.nao_terminais:
            follow[nt] = self.__followpos_nt(nt)
        return follow
    
    # Abreviacao de um monte de coisa
    def tratada(self):
        return self.sem_recursao().fatorada().sem_inalcancaveis()

if __name__ == "__main__":  
    gn = Gramatica().from_file("gramatica_ex4.txt")
    print(gn)
    print("--------------")
    # print(gn.e_livre().sem_inalcancaveis())
    g1 = gn.sem_recursao()
    print(g1)
    print("--------------")
    g2 = g1.fatorada()
    print(g2)
    # g1 = gn.sem_recursao()
    # print(g1)
    # g2 = g1.fatorada()
    # print(g2)
    # for _ in range(100):
    #     print(g.generate_word())
    # print(g)
    # print("-----------------------------")
    # print(g.tratada())
    # print(g.sem_recursao())
    # for producoes in c.producoes.values():
    #     print([type(producao) for producao in producoes])
    # print(c)