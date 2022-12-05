from random import randrange
from string import ascii_uppercase

class Production(str):
    def __init__(self, conteudo: str, separation_par = "char", nt_identification = None):
        self.conteudo = conteudo
        self.separation_par = separation_par #char ou space
        self.nt_identification = None #caracteres especiais no inicio e fim de nao terminais
        
    def __iter__(self):
        if self.separation_par == "space":
            return iter(self.conteudo.split())
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
            saida += f"{nao_terminal} -> {producoes}\n"
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
            for linha in arquivo:
                nao_terminal, producoes = [palavra.strip() for palavra in linha.split("->")]
                
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
                            # TODO: Deve haver algum jeito melhor de diferenciar terminal e nao terminal
                            if simbolo == simbolo.lower():
                                if not simbolo in self.terminais: self.terminais.append(simbolo)
                            else:
                                if not simbolo in self.nao_terminais: self.nao_terminais.append(simbolo) 
                        else:
                            if self.nt_identification[0] in simbolo:
                                if not simbolo in self.nao_terminais: self.nao_terminais.append(simbolo)
                            else:
                                if not simbolo in self.terminais: self.terminais.append(simbolo)
                            
        return self

    # Escreve a gramatica num arquivo
    def to_file(self, filename: str):
        with open(filename, "w") as arquivo:
            for nao_terminal, producoes in self.producoes.items():
                producoes = " | ".join(producoes)
                arquivo.write(f"{nao_terminal} -> {producoes}")

    # Retorna um novo nao terminal 
    def novo_nao_terminal(self, original = None):
        
        if self.nt_identification is None:
            # Tenta retornar uma letra do alfabeto
            alfabeto = list(ascii_uppercase)
            for letra in alfabeto:
                if not letra in self.nao_terminais:
                    self.nao_terminais.append(letra)
                    return letra
            
            # TODO: Geracoes mais iradas
            # Tenta acentuar a letra 
            raise RuntimeError("NAO CONSIGO RESTORNAR MAIS")
        else:
            return original[:-1]+"1"+original[-1]

    # Simplesmente retorna uma producao aleatoria dentre as possiveis
    def random_production(self, nao_terminal: str) -> str:
        producao = self.producoes[nao_terminal][randrange(len(self.producoes[nao_terminal]))]
        if producao == "&":
            return ""
        else:
            return producao

    # Gera uma palavra aleatoria da gramatica
    def generate_word(self):
        forma_sentencial = self.inicial

        # Ao inves de um while eh um for com limite de 100 iteracoes pra n ir pra sempre
        for _ in range(100):
            for simbolo in forma_sentencial:
                if simbolo in self.nao_terminais:
                    indice = forma_sentencial.index(simbolo)
                    forma_sentencial = forma_sentencial[:indice] + self.random_production(simbolo) + forma_sentencial[indice+1:]
                    break
            else:
                break
        return forma_sentencial

    # Altera a gramatica alterando as producoes da cabeca pra que "incorporem" as producoes do corpo e o eliminem
    def herdar_producoes(self, nt_cabeca: str, nt_corpo: str):
        # print(nt_cabeca, nt_corpo)
        novas_producoes = []
        for producao in self.producoes[nt_cabeca]:
            destruir = 0
            for index, simbolo in enumerate(producao):
                if simbolo == nt_corpo:
                    destruir += 1
                    if destruir > 1:
                        raise RuntimeError(f"POISE O SIMBOLO PRA HERDAR APARECEU 2 VEZES EM {producao}")
                    for herdada in self.producoes[nt_corpo]:
                        if herdada == "&":
                            if len(producao) > 1:
                                novas_producoes.append(producao[:index]+producao[index+1:])
                            elif not "&" in self.producoes[nt_cabeca]:
                                novas_producoes.append("&")
                        else:
                            novas_producoes.append(producao[:index]+herdada+producao[index+1:])
            if destruir == 1:
                self.producoes[nt_cabeca].remove(producao)
        self.producoes[nt_cabeca] += novas_producoes
                    
    # Retorna a gramatica sem epslon producoes
    def e_livre(self):
        copia: Gramatica = self.copy()

        # Encontra os simbolos anulaveis
        anulaveis = ["&"]
        alterado_flag = True
        while alterado_flag:
            # Flag pra ver se algum nao terminal passou a ser anulavel nessa iteracao
            alterado_flag = False
            for nao_terminal, producoes in copia.producoes.items():
                
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
        
        # Novo estado inicial caso necessario
        if copia.inicial in anulaveis:
            novo_inicial = copia.novo_nao_terminal()
            copia.producoes[novo_inicial] = [copia.inicial, "&"]
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
                if len(producao) == 1:
                    continue
                for index, simbolo in enumerate(producao):
                    if simbolo in anulaveis:
                        producoes.append(producao[:index]+producao[index+1:])
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
        self.producoes[novo_simbolo] = ["&"]

        self.producoes[nao_terminal] = [producao+novo_simbolo for producao in producoes_nao_recursivas]
        self.producoes[novo_simbolo] += [producao[1:]+novo_simbolo for producao in producoes_recursivas]

    # Retorna a gramatica sem recursao a esquerda
    def sem_recursao(self):
        copia = self.copy().sem_loop().e_livre()

        # Notacao dos slides da professora
        for i, ai in enumerate(copia.nao_terminais):
            
            # Eliminacao da recursao indireta
            for _, aj in zip(range(i), copia.nao_terminais):
                for pi in copia.producoes[ai]:
                    if pi[0] == aj:
                        for pj in copia.producoes[aj]:
                            copia.producoes[ai].append(pj+pi[1:])
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
                    self.producoes[novo_nt] = [producao[1:] for producao in self.producoes[nao_terminal] if self.producoes[nao_terminal].index(producao) in indices]
                    for producao in self.producoes[novo_nt]:
                        if producao == "":
                            self.producoes[novo_nt].remove("")
                            self.producoes[novo_nt].append("&")

                    # Elimina as producoes nao deterministicas
                    for offset, indice in enumerate(indices):
                        self.producoes[nao_terminal].pop(indice-offset)

                    # Transicao que leva pro novo nao terminal
                    self.producoes[nao_terminal].append(simbolo+novo_nt)

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
    def fatorada(self):
        copia = self.copy()
        # Elimina ND direto iniciais
        for nao_terminal in copia.nao_terminais:
            copia.eliminar_nd_direto(nao_terminal)
        
        # TODO: POSSIVEL PROBLEMA PRA GRAMATICAS COMPLEXAS
        # Se ha nao terminal a esquerda entao ta na hora de herdar producao
        nt_lista = list(copia.producoes.keys())
        for nao_terminal in nt_lista:
            for i in range(100):
                for producao in copia.producoes[nao_terminal]:
                    # Comeca de fato com um nao terminal
                    if producao[0] in copia.nao_terminais:
                        copia.herdar_producoes(nao_terminal, producao[0])
                        break
                else:
                    # Se ele nao conseguiu herdar nada
                    break
            novo_nt = copia.eliminar_nd_direto(nao_terminal)
            if novo_nt:
                nt_lista.append(novo_nt)

    # Retorna a gramatica sem producoes unitarias
    def sem_unitarias(self):
        pass

g = Gramatica().from_file("gramatica_indireta.txt")
print(g)
print("-----------------------------")
g.fatorada()
print(g)
# print(g.sem_recursao())
# for _ in range (20):
#     print(g.generate_word())