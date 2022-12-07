from random import randrange
from string import ascii_uppercase

class Production(str):
    def __init__(self, conteudo: str, separation_par = "space", nt_identification = None):
        self.conteudo = conteudo.strip().split()
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
    def novo_nao_terminal(self, original = None, first = False):
        alfabeto = list(ascii_uppercase)
        found = False
        sufix = 0
        for _ in range(10000):
        # Tenta retornar uma letra do alfabeto
            if not original is None:
                proposta = original+"".join(["'" for _ in range(sufix)])
                if not proposta in self.nao_terminais:
                    break
            else:
                for letra in alfabeto:
                    proposta = letra+"".join(["'" for _ in range(sufix)])
                    if not proposta in self.nao_terminais:
                        found = True
                        break
            if found: break
            sufix += 1
        else: 
            raise RuntimeError("Nao consegui gerar um nome novo")
        # print(self.nao_terminais)
        # print(proposta)
        if not first:
            self.nao_terminais.append(proposta)
        else:
            self.nao_terminais.insert(0, proposta)
        return proposta

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

    # Retorna se ha ou nao nd_indireto neste nao terminal
    def ha_nd_indireto(self, nt, derivaveis = None):
        if derivaveis == None:
            derivaveis = set()
        derivaveis.add(nt)
        # Olha todos os simbolos da producao
        for producao in self.producoes[nt]:
            # Se o simbolo da producao ja foi encontrado como derivavel
            if producao[0] == nt:
                print(self)
                raise RuntimeError("RECURSAO INDIRETA")
            for simbolo in producao:
                # Simbolo repetido
                if simbolo in derivaveis:
                    return True

                anulaveis = self.anulaveis()
                # Terminal novo
                if simbolo in self.terminais:
                    derivaveis.add(simbolo)
                    break 
                # Nao terminal novo
                elif simbolo in self.nao_terminais:
                    ha_nd_derivado = self.ha_nd_indireto(simbolo, derivaveis)
                    # Se consegue derivar algo ja derivado
                    if ha_nd_derivado:
                        return True
                    # Se o simbolo nao eh anulavel nao tem que ver os proximos, se eh tem
                    if not simbolo in anulaveis:
                        break
        return False
            
    # Marca simbolos alcancaveis
    def alcance(self, nao_terminal):
        for producao in self.producoes[nao_terminal]:
            for simbolo in producao:
                if simbolo in self.nao_terminais:
                    if not self.alcancavel[simbolo]:
                        self.alcancavel[simbolo] = True
                        self.alcance(simbolo)

    # (ALTERA) Elimina simbolos inalcancaveis
    def sem_inalcancaveis(self):
        # copia = self.copy()
        self.alcancavel = {nt: False for nt in self.nao_terminais}
        self.alcancavel[self.inicial] = True
        self.alcance(self.inicial)
        for nt in self.alcancavel:
            if not self.alcancavel[nt]:
                self.nao_terminais.remove(nt)
                self.producoes.pop(nt)
        return self
        # return copia

    # Como herdar_producoes mas restrito a apenas o primeiro simbolo da producao
    def herdar_primeiro(self, nt_cabeca: str, nt_corpo: str):
        # print(nt_cabeca, "herda", nt_corpo)
        novas_producoes = []
         # Itera sobre cada producao
        for producao in self.producoes[nt_cabeca]:

            # Simbolo inicial eh o que vai ser substituido por suas producoes
            if producao[0] == nt_corpo:
                for herdada in self.producoes[nt_corpo]:
                    if herdada == "&":
                        if len(producao) > 1:
                            if producao[1:] != nt_cabeca:
                                novas_producoes.append(Production((" ".join(producao[1:]).strip())))
                        else:
                            novas_producoes.append(Production("&"))
                    else:
                        nova_prod = (herdada+" "+" ".join(producao[1:])).strip()
                        novas_producoes.append(Production(nova_prod))
                self.producoes[nt_cabeca].remove(producao)
        
        # self.producoes[nt_cabeca] += novas_producoes
        for producao in novas_producoes:
            if not producao in self.producoes[nt_cabeca] and producao != nt_cabeca:
                # print(producao, self.producoes[nt_cabeca])
                self.producoes[nt_cabeca].append(producao)
    
    # OBSOLETO
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
                                novas_producoes.append(Production((" ".join(producao[:index])+" "+" ".join(producao[index+1:]).strip())))
                            else:
                                novas_producoes.append(Production("&"))
                        else:
                            novas_producoes.append(Production((" ".join(producao[:index])+" "+herdada+" "+" ".join(producao[index+1:])).strip()))
            if destruir == 1:
                self.producoes[nt_cabeca].remove(producao)
        # self.producoes[nt_cabeca] += novas_producoes
        for producao in novas_producoes:
            if not producao in self.producoes[nt_cabeca]:
                # print(producao, self.producoes[nt_cabeca])
                self.producoes[nt_cabeca].append(producao)

     # (ALTERA)Retorna a gramatica sem producoes unitarias
    def sem_unitarias(self, ignore_first = False):
        # copia = self.copy()
        for nao_terminal, producoes in self.producoes.items():
            if ignore_first and nao_terminal == self.inicial:
                continue
            herdados = set()
            houve_alteracao = True
            while houve_alteracao:
                houve_alteracao = False
                for producao in producoes:
                    if len(producao) == 1 and producao[0] in self.nao_terminais and not producao[0] in herdados:
                        self.herdar_primeiro(nao_terminal, producao[0])
                        houve_alteracao = True
                        herdados.add(producao[0])
                        # break
                # print("---------------")
                # print(self)
        return self

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
    def e_livre(self, inicial_novo = True):
        # copia: Gramatica = self.copy()

        # Encontra os simbolos anulaveis
        anulaveis = self.anulaveis()
        
        # Novo estado inicial caso necessario
        if self.inicial in anulaveis:
            if inicial_novo:
                novo_inicial = self.novo_nao_terminal(first = True)
                self.producoes[novo_inicial] = [Production(self.inicial), Production("&")]
                self.inicial = novo_inicial

                # Refaz o dicionario pro novo inicial vir primeiro
                novas_producoes = {novo_inicial: self.producoes[novo_inicial]}
                for nt in self.nao_terminais:
                    novas_producoes[nt] = self.producoes[nt]
                self.producoes = novas_producoes

            else:
                if not "&" in self.producoes[self.inicial]:
                    self.producoes[self.inicial].append(Production("&"))
        
        # Elimina as & producoes
        for nao_terminal, producoes in self.producoes.items():
            if nao_terminal == self.inicial:
                continue
            if "&" in producoes:
                producoes.remove("&")

        # Gera as producoes livres
        for nao_terminal, producoes in self.producoes.items():
            for producao in producoes:
                # print(nao_terminal, producoes)
                if len(producao) == 1:
                    continue
                for index, simbolo in enumerate(producao):
                    # print(index, simbolo)
                    if simbolo in anulaveis:
                        # print(simbolo, "lista",list(producao), producao[index+1:])
                        nova_prod = Production((" ".join(producao[:index])+" "+" ".join(producao[index+1:])).strip())
                        # print(nova_prod)
                        if not nova_prod in producoes:
                            producoes.append(nova_prod)
        return self

    # Retorna um conjunto com todos nao terminais que o nao terminal chega atraves de producoes unitarias (usada pra detectar loops)
    def unitary_reach(self, nt: str, alcance_unitario = None):
        if alcance_unitario is None:
            alcance_unitario = set()
        alcance_unitario.add(nt)
        for producao in self.producoes[nt]:
            if producao in self.nao_terminais and not producao in alcance_unitario:
                alcance_unitario.add(str(producao))
                alcance_unitario.union(self.unitary_reach(producao, alcance_unitario))
        return alcance_unitario
    
    # Substitui em todas as producoes um simbolo velho por um novo
    def substitute(self, old: str, new: str):
        old = " "+old+" "
        new = " "+new+" "
        for nt, producoes in self.producoes.items():
            for producao in producoes.copy():
                # print(producao,"-", old,"-", old in " "+producao+" ")
                if old in " "+producao+" ":
                    nova_producao = (" "+producao+" ").replace(old, new)
                    self.producoes[nt].remove(producao)
                    self.producoes[nt].append(Production(nova_producao.strip()))
            
    # Retorna a gramatica sem loops
    def sem_loop(self):
        # copia = self.copy()
        
        # Tratamento de loops diretos
        for nt, producoes in self.producoes.items():
            if nt in producoes:
                producoes.remove(nt)
        
        # Tratamento de loops nao diretos
        for nt1 in self.nao_terminais:
            for nt2 in self.nao_terminais.copy():
                if nt1 == nt2:
                    continue
                if nt1 in self.unitary_reach(nt2) and nt2 in self.unitary_reach(nt1):
                    # print(nt1, nt2)
                    self.herdar_primeiro(nt1, nt2)
                    self.substitute(nt2, nt1)
                    # Elimina loops triviais criados
                    for producao in self.producoes[nt1]:
                        if producao == nt1:
                            self.producoes[nt1].remove(producao)
                    self.sem_inalcancaveis()
                    # print("-----------")
                    # print(copia)
                    # raise RuntimeError
        # print("----------------")   
        
        return self

    # Altera a gramatica para retirar recursao direta daquele nao terminal
    def eliminar_recursao_direta(self, nao_terminal: str):
        
       # Separa producoes recursivas de nao recursivas
        producoes_recursivas = []
        producoes_nao_recursivas = []
        # print(self.producoes[nao_terminal])
        for producao in self.producoes[nao_terminal]:
            if nao_terminal != producao[0]:
                producoes_nao_recursivas.append(producao)
            if nao_terminal == producao[0]:
                producoes_recursivas.append(producao)

        # print(producoes_nao_recursivas, producoes_recursivas)

        # Se nao ha producoes recursivas nao ha o que fazer
        if len(producoes_recursivas) == 0:
            return

        # Eliminacao de recursoes diretas
        novo_simbolo = self.novo_nao_terminal(nao_terminal)
        self.producoes[novo_simbolo] = [Production("&")]

        self.producoes[nao_terminal] = []
        for producao in producoes_nao_recursivas:
            # Corner case, talvez o & tenha que continuar mas acho que nao
            if producao == "&":
                self.producoes[nao_terminal].append(Production(novo_simbolo))
                continue

            self.producoes[nao_terminal].append(Production(producao+" "+novo_simbolo))
        # if novo_simbolo == "C'": print("AQUI")
        self.producoes[novo_simbolo] += [Production(" ".join(producao[1:])+" "+novo_simbolo) for producao in producoes_recursivas]
        # print(self.producoes[novo_simbolo])

    # Retorna a gramatica sem recursao a esquerda
    def sem_recursao(self):
        self = self.tratamento_1()
        # Notacao dos slides da professora
        for i, ai in enumerate(self.nao_terminais):
            
            # Eliminacao da recursao indireta
            for _, aj in zip(range(i), self.nao_terminais):
                for pi in self.producoes[ai]:
                    # print("bate?",aj, pi)
                    if pi[0] == aj:
                        # print(ai,"herda", aj)
                        for pj in self.producoes[aj]:
                            if pj != "&":
                                self.producoes[ai].append(Production((pj+" "+" ".join(pi[1:])).strip()))
                            else:
                                self.producoes[ai].append(Production(" ".join(pi[1:])))
                            # print("iterando:", copia.producoes[ai])
                        # print("fim:", copia.producoes[ai])
                        self.producoes[ai].remove(pi)
                        # print("HERDEI---------------------")
                        # print(self)
            
            def tratamento_improvisado(nt):
                # Eliminacao de loops e producoes unitarias criadas
                for producao in self.producoes[nt]:
                    if len(producao) == 1 and producao in self.nao_terminais:
                        # print("tratamento:",nt, producao)
                        if producao == nt:
                            self.producoes[nt].remove(producao)
                        else:
                            self.herdar_primeiro(nt, producao)

            # Eliminacao da recursao direta
            # print(ai, "------------")        
            # print(self)
            # tratamento_improvisado(ai)
            self.eliminar_recursao_direta(ai)
            # tratamento_improvisado(ai)

            # Elimina producoes unitarias

            # copia = copia.sem_loop()

        return self

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
                    novo_nt = self.novo_nao_terminal(nao_terminal)
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
         
    # Retorna a gramatica fatorada
    def fatorada(self):
        # print("1--------")
        # print(self)
        # Elimina ND direto iniciais
        for nao_terminal in self.nao_terminais:
            self.eliminar_nd_direto(nao_terminal)
        # print("2------")
        # print(self)
        # print("3--------")
        
        # TODO: POSSIVEL PROBLEMA PRA GRAMATICAS COMPLEXAS
        # Se ha nao terminal a esquerda entao ta na hora de herdar producao
        nt_lista = list(self.producoes.keys())

        for nao_terminal in nt_lista:
            
            for _ in range(100):

                # Guarda p/ crescimento muito grande
                if len(self.producoes[nao_terminal]) > 100:
                    raise RuntimeError("Nao consegui fatorar a gramatica (muita producao)")

                # TODO: VER SE VALE USAR ISSO OU NAO 
                # Nao ha nd indireto a ser resolvido
                # if not self.ha_nd_indireto(nao_terminal):
                #     break

                # Itera sobre as producoes herdando todos os iniciais sempre que possivel
                for producao in self.producoes[nao_terminal]:
                    # Comeca de fato com um nao terminal
                    if producao[0] in self.nao_terminais:
                        # print(nao_terminal, producao[0], list(producao))
                        self.herdar_primeiro(nao_terminal, producao[0])
                        break
                # Se ele nao conseguiu herdar nada
                else: 
                    break
            else:
                raise RuntimeError("Nao consegui fatorar a gramatica (limite de derivacoes)")
            
            # Elimina ND direto gerado 
            novo_nt = self.eliminar_nd_direto(nao_terminal)
            if novo_nt:
                nt_lista.append(novo_nt)
        
        return self

    # Retorna o firstpos de uma producao
    def first_prod(self, producao: Production):
        print("prod:", producao)
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
    
    # Tira loops e e producoes da gramatica e verifica ambiguidade
    def tratamento_1(self):
        self.e_livre()
        self.sem_loop()
        for nt, producoes in self.producoes.items():
            for producao in producoes:
                if producao[0] == nt and len(producao) > 1 and len(set(list(producao))) == 1:
                    # Producao do tipo S -> S S S S que eh ambigua inerentemente
                    raise SyntaxError(f"Gramatica ambigua {nt} -> {producao}")
        return self


    # Abreviacao de um monte de coisa
    def tratada(self):
        return self.sem_recursao().fatorada().sem_inalcancaveis()

if __name__ == "__main__":  
    g = Gramatica().from_file("gramatica_ex4.txt")
    print(g)
    # print("-------e livre-------")
    # g.e_livre()
    # print(g)
    # print("----sem loop----")
    # g.sem_loop()
    # print(g)
    print("-------sem rec-------")
    g.sem_recursao()
    print(g)
    print("-----fatorada----")
    g.fatorada()
    print("f:",g)
    # g2 = g1.fatorada()
    # print(g2)
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