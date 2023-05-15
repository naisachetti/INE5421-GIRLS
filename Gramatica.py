from random import randrange
from string import ascii_uppercase

class Nodo:
    def __init__(self, grammar, simbolo: str, pai, folhas: list, anulaveis: list, debt: list = None):
        self.simbolo = simbolo
        self.pai = pai
        self.folha = simbolo in grammar.terminais and simbolo != "&"
        self.filhos = []
        if self.folha:
            folhas.append(self)
            return
        # Caso especial que envolve debito de followpos
        if simbolo == "&":
            if not len(debt):
                pass
            # Followpos com simbolo inicial nao anulavel
            elif not debt[0] in anulaveis:
                self.filhos.append(Nodo(grammar, debt[0], self, folhas, anulaveis))
            # Passa o restante do debito
            else:
                self.filhos.append(Nodo(grammar, debt[0], self, folhas, anulaveis, debt[1:]))
            # print(self)
            return
        for producao in grammar.producoes[simbolo]:
            # Tratamento simples para simbolos nao anulaveis
            if not producao[0] in anulaveis:
                self.filhos.append(Nodo(grammar, producao[0], self, folhas, anulaveis))
                continue

            # Simbolo nao terminal anulavel
            if debt is None: debt = producao[1:]
            self.filhos.append(Nodo(grammar, producao[0], self, folhas, anulaveis, debt))
        # print(self)
    def __repr__(self):
        return f"{None if self.pai is None else self.pai.simbolo} -> {self.simbolo}{'' if not len(self.filhos) else f' -> {[filho.simbolo for filho in self.filhos]}'}"

class ArvoreAuxiliar:
    def __init__(self, grammar, raiz: str, anulaveis: list) -> None:
        self.folhas = []
        self.raiz: str = Nodo(grammar, raiz, None, self.folhas, anulaveis)
        self.nd = False
        self.folhas_simbolos = [folha.simbolo for folha in self.folhas]
        for simbolo in self.folhas_simbolos:
            if self.folhas_simbolos.count(simbolo) > 1:
                self.nd = True
                break
    
    def derivacoes_ate(self, simbolo: Nodo):
        path = [simbolo]
        while not simbolo.pai is None:
            path.insert(0,simbolo.pai)
            simbolo = simbolo.pai
        return path
    
    def ancestral_comum_derivativo(self, terminal: str):
        # Guarda simples
        if self.folhas_simbolos.count(terminal) == 1:
                return None, None

        ocorrencias = list(filter(lambda e: e.simbolo == terminal, self.folhas))
        
        caminhos = [self.derivacoes_ate(ocorrencia) for ocorrencia in ocorrencias]
        caminho_comum = set(caminhos[0])
        for i, caminho in enumerate(caminhos):
            if not i: continue
            caminho_comum.intersection_update(set(caminho))
        
        for caminho in caminhos:
            for comum in caminho_comum:
                caminho.remove(comum)

        caminho_raiz = self.derivacoes_ate(ocorrencias[0])
        for nodo in caminhos[0]:
            caminho_raiz.remove(nodo)
        
        return caminho_raiz, caminhos
        
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
    
    def __contains__(self, __key: str) -> bool:
        return __key in self.conteudo

    def index(self, valor) -> int:
        # print(self.conteudo, valor)
        return self.conteudo.index(valor)

class Preprocessor:
    def __init__(self) -> None:
        self.starting_symbol: str = None

    # Recebe uma producao e o indice de um simbolo depois de um parenteses (pode ser len da producao)
    # Retorna o indice do parenteses que completa ele
    def get_simbol_context(self, producao: list, index: int) -> int:
        scope_count = 0
        for i in range(index-1, -1, -1):
            if producao[i] == ")": scope_count -= 1
            elif producao[i] == "(": scope_count += 1
            if scope_count == 0:
                return i
        raise RuntimeError(f"Nao consegui parsear essa producao: {producao}")
    
    # Recebe um simbolo e coloca ele no fim de cada sequencia num |
    def spread_symbol_right(self, corte: list, inserido: str):
        corte = corte.copy()
        flag = False
        for index, simbolo in enumerate(corte):
            if flag:
                flag = False
                continue
            if simbolo == "|":
                corte.insert(index, inserido)
                flag = True
        corte.append(inserido)
        return corte

    # Recebe um arquivo com a gramtica, processa e escreve num arquivo <gramatica>_post
    def from_file(self, filename: str):
        aux = 0
        grammar = []
        # Simplesmente Le o arquivo
        with open(filename, "r") as arquivo:
            for linha in arquivo:
                nt, producao = linha.split("::=")
                nt = nt.strip()
                producao = [elemento.strip() for elemento in producao.split()]
                grammar.append([nt, producao])

        self.starting_symbol = grammar[0][0]

        delete_stack = []

        # Processa coisas entre () que nao tem simbolos ? + * depois, normalmente eh so um OU
        for linha in grammar:
            nt, producao = linha
            for index, simbolo in enumerate(producao):
                if simbolo == ")" and ((index != len(producao)-1 and producao[index+1] not in {"?", "*", "+"}) or index == len(producao)-1):
                    scope_start = self.get_simbol_context(producao, index + 1)
                    corte = producao[scope_start+1:index]
                    grammar.append([nt, producao[:scope_start]+[f"AUX{aux}"]+producao[index+1:]])
                    grammar.append([f"AUX{aux}"] + [corte])
                    delete_stack.append(linha)
                    aux += 1
                    break
        for linha in delete_stack:
            grammar.remove(linha)

        # Linhas a serem deletadas depois de iterar tudo pq n se deleta elementos de um iterador enquanto se itera sobre ele
        delete_stack = []

        # Processa os simbolos "? + *"
        for linha in grammar:
            nt, producao = linha
            for index, simbolo in enumerate(producao):
                if simbolo in {"?", "*", "+"}:
                    scope_start = self.get_simbol_context(producao, index)
                    corte = producao[scope_start+1:index-1]
                    grammar.append([nt, producao[:scope_start]+[f"AUX{aux}"]+producao[index+1:]])
                    if simbolo == "?":
                        grammar.append([f"AUX{aux}"] + [corte + ["|", "&"]])
                    elif simbolo == "*":
                        grammar.append([f"AUX{aux}"] + [self.spread_symbol_right(corte, f"AUX{aux}") + ["|", "&"]])
                    elif simbolo == "+":
                        grammar.append([f"AUX{aux}"] + [self.spread_symbol_right(corte, f"AUX{aux}") + ["|"] + corte])
                    delete_stack.append(linha)
                    aux += 1
                    break
        for linha in delete_stack:
            grammar.remove(linha) 
    
        # AQUI A GRAMATICA JA TA PRE PROCESSADA

        mapeamento = {"\*": "*", "\+": "+", "\)": ")", "\(": "("}

        for nt, producoes in grammar:
            for i, simbolo in enumerate(producoes):
                if simbolo in mapeamento:
                    producoes[i] = mapeamento[simbolo]

        with open(f"{filename}_post", "w") as arquivo:

            # Escreve a primeira producao primeiro, isso eh importante
            for nt, producoes in grammar:
                if nt == self.starting_symbol:
                    arquivo.write(f"{nt} ::= {' '.join(producoes)}\n")
                    break 

            # Escreve o resto
            for nt, producoes in grammar:
                if nt == self.starting_symbol: continue
                arquivo.write(f"{nt} ::= {' '.join(producoes)}\n")                    

class Gramatica:
    
    # Inicia a gramatica
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

    # Le a gramatica a partir de um arquivo mas tenta pre processala antes
    def from_file_preprocess(self, filename: str):
        Preprocessor().from_file(filename)
        return self.from_file(f"{filename}_post")
    
    # Le a gramatica de um arquivo
    def from_file(self, filename: str):
        with open(filename, "r") as arquivo:

            conjunto_simbolos = set()

            for linha in arquivo:
                # Ignora linhas vazias
                if linha.strip() == "":
                    continue

                separador = "->" if "->" in linha else "::="
                nao_terminal, producoes = [palavra.strip() for palavra in linha.split(separador)]

                # Simbolo inicial da gramatica
                if self.inicial == None:
                    self.inicial = nao_terminal

                # Adiciona nao terminal na lista
                if not nao_terminal in self.nao_terminais: self.nao_terminais.append(nao_terminal)

                producoes = list({Production(palavra.strip()) for palavra in producoes.split("|")})

                # Criacao dos dicionarios
                self.producoes[nao_terminal] = producoes

                # Leitura de todos os simbolos novos
                for producao in producoes:
                    for simbolo in producao:

                        # Assume que nao terminais sao um unico caracter identificado por ser letra maiuscula
                        conjunto_simbolos.add(simbolo)

            # Criacao dos simbolos nao terminais
            for simbolo in conjunto_simbolos.copy():
                if simbolo in self.nao_terminais:
                    conjunto_simbolos.remove(simbolo)
                self.terminais = list(conjunto_simbolos)
        self.to_file("debug/source")
        return self

    # Escreve a gramatica num arquivo
    def to_file(self, filename: str):
        with open(filename, "w") as arquivo:
            for nao_terminal, producoes in self.producoes.items():
                producoes = " | ".join(producoes)
                arquivo.write(f"{nao_terminal} ::= {producoes}\n")

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
            for simbolo in forma_sentencial:
                if simbolo in self.nao_terminais:
                    indice = forma_sentencial.index(simbolo)
                    nova_prod = self.random_production(simbolo)
                    forma_sentencial = Production(" ".join(forma_sentencial[:indice])+" "+nova_prod+" "+" ".join(forma_sentencial[indice+1:]))
                    break
            # Se entrou no else a forma sentencial eh na vdd uma sentenca
            else:
                break
        # Se entrou no else ele n conseguiu gerar uma sentenca
        else:
            return None
        # Retorna a forma sentencial com o simbolo de fim de sentenca no final
        return Production(" ".join(forma_sentencial)+" $")
    
    ################ Alteracao fundamentais da gramatica ################

    # Retorna um novo nao terminal
    def novo_nao_terminal(self, original: str = None, first: bool = False):
        alfabeto = list(ascii_uppercase)
        found = False
        sufix = 1
        if not original is None and "'" in original:
            original = original[:original.index("'")]
        for _ in range(10000):
            # Tenta retornar o original com um 'X
            if not original is None:
                proposta = original + "'" + str(sufix)
                # Proposta eh um simbolo novo
                if not proposta in self.nao_terminais:
                    break
            else:
                # Tenta retornar uma letra do alfabeto nao usada, e enche coloca 'X se necessario
                for letra in alfabeto:
                    proposta = letra + "'" + str(sufix)
                    # Proposta eh um simbolo novo
                    if not proposta in self.nao_terminais:
                        found = True
                        break

            # Eis que tu quer dar break 2 vezes pra sair de um for dentro do outro
            if found: break

            # Aumenta o numero de '
            sufix += 1
        else:
            raise RuntimeError("Nao consegui gerar um nome novo")

        # Coloca o novo nao terminal na lista de nao terminais
        if not first:
            self.nao_terminais.append(proposta)
        else:
            self.nao_terminais.insert(0, proposta)
        return proposta

    # Substitui em todas as PRODUCOES um simbolo velho por um novo
    def substitute(self, old: str, new: str):
        if old == new: return
        # Tratamento assumindo que simbolos sao separados por espacos
        old = " "+old+" "
        new = " "+new+" "
        for nt, producoes in self.producoes.items():
            for producao in producoes.copy():
                if old in " "+producao+" ":
                    # Se o simbolo antigo esta na producao o substitui pelo novo
                    nova_producao = (" "+producao+" ").replace(old, new)
                    self.producoes[nt].remove(producao)
                    self.producoes[nt].append(Production(nova_producao.strip()))

    # Substitui em toda gramatica um simbolo velho por um novo
    def update_symbol(self, old: str, new: str):
        if old == new: return
        self.substitute(old, new) #Substitui nas producoes
        # Atualiza um terminal
        if old in self.terminais:
            self.terminais.remove(old)
            self.terminais.append(new)
            return self
        
        # Nao terminal nao inicial
        if old != self.inicial:
            self.producoes[new] = self.producoes[old]
            self.producoes.pop(old)

            self.nao_terminais.append(new)
            self.nao_terminais.remove(old)
            return self
        
        # O simbolo incial tem que ser o primeiro do dicionario
        self.inicial = new

        self.nao_terminais.insert(0, new)
        self.nao_terminais.remove(old)

        novas_producoes = {new: self.producoes[old]}
        self.producoes.pop(old)
        novas_producoes.update(self.producoes)
        self.producoes = novas_producoes
        
    # Substitui o simbolo nt_corpo por suas producoes se for o primeiro de um producao do nt_cabeca
    def herdar_primeiro(self, nt_cabeca: str, nt_corpo: str):

        # Lista auxiliar com as novas producoes
        novas_producoes = []

        # Itera sobre cada producao
        for producao in self.producoes[nt_cabeca].copy():
            if producao[0] != nt_corpo: continue

            # Itera sore as producos do simbolo "herdado"
            for herdada in self.producoes[nt_corpo]:

                # Simbolo herdado eh anulavel (n acontece se ja for e-livre)
                if herdada == "&":
                    # Anula o simbolo
                    if len(producao) > 1:

                        # Impede a criacao de loops
                        if producao[1:] == nt_cabeca: continue

                        # Simplesmente recoloca a producao sem o nt_corpo
                        novas_producoes.append(Production((" ".join(producao[1:]).strip())))
                    # O nt_cabeca eh anulavel pq tinha producao unitaria pro corpo
                    else:
                        novas_producoes.append(Production("&"))
                else:
                    # Cria a nova producao
                    nova_prod = (herdada+" "+" ".join(producao[1:])).strip()
                    novas_producoes.append(Production(nova_prod))

            self.producoes[nt_cabeca].remove(producao)

        # Incorpora novas producoes se nao forem repetiras ou loops (sim ele impede loops 2 vezes eu odeio loops)
        for producao in novas_producoes:
            if not producao in self.producoes[nt_cabeca] and producao != nt_cabeca:
                self.producoes[nt_cabeca].append(producao)
    
    # Retira producoes diretas da gramatica (NT0 -> a b c d NT1)
    def sem_diretas(self):
        for nt in self.nao_terminais:
            # Apenas uma producao
            if len(self.producoes[nt]) != 1: continue
            # Fecha com NT
            # if not self.producoes[nt][0][-1] in self.nao_terminais: continue
            # Soh terminal no caminho
            # if len(set(self.producoes[nt][0][:-1]).difference(set(self.terminais))): continue
            # Impede de fazer isso com uma producao semi recursiva
            if nt in self.producoes[nt][0]: continue
            # Realiza a sobstituicao da producao simples
            self.substitute(nt, self.producoes[nt][0])

        self.sem_inalcancaveis()
        return self

    # Minimiza o numero de apostrofos
    def pretify(self):
        # Reduz o numero de simbolos tipo S S'3 S'10 pro minimo
        simbolos_sem_apostrofe = set(map(lambda e: e if not "'" in e else e[:e.index("'")], self.nao_terminais))
        for simbolo in simbolos_sem_apostrofe:
            ocorrencias = list(filter(lambda e : simbolo == (e if not "'" in e else e[:e.index("'")]) , self.nao_terminais))
            ocorrencias.sort(key=lambda e: -1 if not "'" in e else int(e[e.rindex("'")+1:]))
            for i, ocorrencia in enumerate(ocorrencias):
                if not i:
                    self.update_symbol(ocorrencia, simbolo)
                    continue
                self.update_symbol(ocorrencia, simbolo+"'"+str(i))
        
        # Renomeacoes pertinentes para gramatica da materia de compiladores
        nts = self.nao_terminais.copy()
        for nt in nts:
            prods = set(map(lambda e: repr(e), self.producoes[nt]))
            if prods == {"-","+"}:
                self.update_symbol(nt, "SIGNAL")
            elif prods == {"/","%","*"}:
                self.update_symbol(nt, "OPERATION")
            elif prods == {"float","string","int"}:
                self.update_symbol(nt, "TYPE")
            elif prods == {">",">=","!=","<","<=","=="}:
                self.update_symbol(nt, "COMPARE")
        
        # Ordena as producoes por ordem alfabetica dos NTs
        nts = self.nao_terminais.copy()
        nts.sort()
        ordenado = {self.inicial: self.producoes[self.inicial]}
        nts.remove(self.inicial)
        ajuntado = {nt: self.producoes[nt] for nt in nts}
        ordenado.update(ajuntado)
        self.producoes = ordenado

        return self

    ##################### &-Producoes #######################

    # Informa se uma forma sentencial eh anulavel
    def nullable_sentence(self, sentence: Production, simbolos_anulaveis: list = None):
        if simbolos_anulaveis is None:
            simbolos_anulaveis = self.anulaveis()
        return len(list(filter(lambda e: e in simbolos_anulaveis, sentence))) != 0     

    # Retorna uma lista com os nao terminais anulaveis da gramatica
    def anulaveis(self):

        # Encontra os simbolos anulaveis
        anulaveis = ["&"]
        # Itera sobre a gramatica ate nao fazer nenhuma modificacao
        alterado_flag = True

        while alterado_flag:
            alterado_flag = False
            for nao_terminal, producoes in self.producoes.items():

                # Se o nao terminal analisado ja eh anulavel nao tem mais o que marcar
                if nao_terminal in anulaveis:
                    continue

                # Itera sobre as producoes da gramatica
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

        # Encontra os simbolos anulaveis da gramatica
        anulaveis = self.anulaveis()

        # Tratamento do simbolo inicial se ele for anulavel
        if self.inicial in anulaveis:

            # Caso necessario, cria um novo simbolo inicial na gramatica
            if inicial_novo:

                # Criacao do novo inicial
                novo_inicial = self.novo_nao_terminal(first = True)
                self.producoes[novo_inicial] = [Production(self.inicial), Production("&")]
                self.inicial = novo_inicial

                # Refaz o dicionario de producoes pro novo inicial vir primeiro (importante pra recursao)
                novas_producoes = {novo_inicial: self.producoes[novo_inicial]}
                for nt in self.nao_terminais:
                    novas_producoes[nt] = self.producoes[nt]
                self.producoes = novas_producoes

            # Se nao ha a criacao de simbolo inicial novo o inicial recebe & (se ta aqui eh pq eh anulavel)
            else:
                if not "&" in self.producoes[self.inicial]:
                    self.producoes[self.inicial].append(Production("&"))

        # Elimina as & producoes de todas as producoes nao iniciais
        for nao_terminal, producoes in self.producoes.items():
            if nao_terminal == self.inicial:
                continue
            if "&" in producoes:
                producoes.remove("&")

        # Gera as producoes livres
        for nao_terminal, producoes in self.producoes.items():
            for producao in producoes:
                # Nao cria producao vazia
                if len(producao) == 1:
                    continue

                # Itera sobre a producao
                for index, simbolo in enumerate(producao):
                    if simbolo in anulaveis:
                        # Cria uma producao nova sem o simbolo anulavel
                        nova_prod = Production((" ".join(producao[:index])+" "+" ".join(producao[index+1:])).strip())
                        if not nova_prod in producoes:
                            producoes.append(nova_prod)
        return self

    ################## Simbolos alcancaveis, loops e producoes unitarias e repetidas #################

    # (Recursiva) Marca nao terminais alcancaveis a partir do informado (nao necessariamente por unitarias)
    def alcance(self, nao_terminal):
        for producao in self.producoes[nao_terminal]:
            for simbolo in producao:
                if simbolo in self.nao_terminais:
                    if not self.alcancavel[simbolo]:
                        self.alcancavel[simbolo] = True
                        self.alcance(simbolo)

    # Elimina simbolos inalcancaveis
    def sem_inalcancaveis(self):
        # Cria o dicionario de nao terminais alcancaveis
        self.alcancavel = {nt: False for nt in self.nao_terminais}
        self.alcancavel[self.inicial] = True
        # Propaga busca da alcancaveis a partir do simbolo inicial
        self.alcance(self.inicial)

        # Itera sobre os nao terminais, removendo os nao alcancaveis
        for nt in self.alcancavel:
            if not self.alcancavel[nt]:
                self.nao_terminais.remove(nt)
                self.producoes.pop(nt)
        return self

    # (Recursiva) Retorna um conjunto com todos nao terminais que o nao terminal chega atraves de producoes unitarias (usada pra detectar loops)
    # TODO: E SE TIVER SIMBOLOS ANULAVEIS?
    def unitary_reach(self, nt: str, alcance_unitario = None):
        if alcance_unitario is None:
            alcance_unitario = set()
        alcance_unitario.add(nt)
        for producao in self.producoes[nt]:
            if producao in self.nao_terminais and not producao in alcance_unitario:
                alcance_unitario.add(str(producao))
                alcance_unitario.union(self.unitary_reach(producao, alcance_unitario))
        return alcance_unitario

    # Retorna a gramatica sem loops
    def sem_loop(self):
        # Tratamento de loops diretos
        for nt, producoes in self.producoes.items():
            if nt in producoes:
                producoes.remove(nt)

        # Tratamento de loops nao diretos
        # Itera sobre todos os pares de nao terminais
        for nt1 in self.nao_terminais:
            for nt2 in self.nao_terminais.copy():
                if nt1 == nt2:
                    continue
                # nt1 e nt2 sao equivalentes
                if nt1 in self.unitary_reach(nt2) and nt2 in self.unitary_reach(nt1):

                    # nt1 herda tudo que nt2 faz e substitui nt2 em todas as producoes
                    self.herdar_primeiro(nt1, nt2)
                    self.substitute(nt2, nt1)

                    # Elimina loops triviais criados
                    for producao in self.producoes[nt1]:
                        if producao == nt1:
                            self.producoes[nt1].remove(producao)

                    # nt2 eh eliminado da gramatica
                    self.sem_inalcancaveis()

        return self

    # Retorna a gramatica sem producoes unitarias
    def sem_unitarias(self, ignore_first = False):
        # Itera sobre toda a gramatica
        for nao_terminal, producoes in self.producoes.items():
            # Se especificado nao altera o simbolo inicial
            if ignore_first and nao_terminal == self.inicial:
                continue

            herdados = set()
            houve_alteracao = True
            # Itera sobre a gramatica ate nao ter mais o que alterar
            while houve_alteracao:
                houve_alteracao = False
                for producao in producoes:
                    # Producao eh unitaria de um nao terminal e ele ja nao herdou o simbolo (n acontece se n tiver loops)
                    if len(producao) == 1 and producao[0] in self.nao_terminais and not producao[0] in herdados:
                        self.herdar_primeiro(nao_terminal, producao[0])
                        houve_alteracao = True
                        herdados.add(producao[0])
                        # break
        return self

    # Tira loops e &-producoes da gramatica e verifica se ha ambiguidade
    def tratamento_1(self):
        self.sem_repeticoes()
        self.e_livre()
        self.sem_loop()
        self.sem_diretas()
        for nt, producoes in self.producoes.items():
            for producao in producoes:
                # print(producao)
                if producao[0] == nt and len(producao) > 1 and len(set(list(producao))) == 1:
                    problema = "!-----gramatica problematica inicio-----!\n"+\
                             repr(self)+\
                            "\n!------gramatica problematica fim------!"
                    # Producao do tipo S -> S S S S que eh ambigua inerentemente
                    raise SyntaxError(f"Gramatica ambigua {nt} -> {producao}\n{problema}")
        self.sem_unitarias()
        self.sem_inalcancaveis()
        self.sem_repeticoes()
        self.pretify()
        self.to_file("debug/e_livre_enxuta")
        return self

    # Tira os nao terminais exatamente iguais com as msms producoes
    def sem_repeticoes(self):
        houve_alteracao = True
        while houve_alteracao:
            houve_alteracao = False
            gram = self.producoes.items()
            for i, (nt_1, producao_1) in enumerate(gram):
                for j, (nt_2, producao_2) in enumerate(gram):
                    if j <= i: continue
                    if producao_1 == producao_2: # Aqui producao eh todas as producoes nao uma soh
                        self.substitute(nt_2, nt_1)
                        houve_alteracao = True
            self.sem_inalcancaveis()
        return self

    ###################### Recursao ##############################

    # Altera a gramatica para retirar recursao direta daquele nao terminal
    def eliminar_recursao_direta(self, nt: str):

        # Separa producoes recursivas de nao recursivas
        producoes_recursivas = []
        producoes_nao_recursivas = []
        for producao in self.producoes[nt]:
            if nt != producao[0]:
                producoes_nao_recursivas.append(producao)
            if nt == producao[0]:
                producoes_recursivas.append(producao)

        # Se nao ha producoes recursivas nao ha o que fazer
        if len(producoes_recursivas) == 0:
            return

        # Criacao do novo nao terminal auxiliar
        novo_simbolo = self.novo_nao_terminal(nt)
        self.producoes[novo_simbolo] = [Production("&")]

        # Apaga as producoes do nao terminal com recursivas
        self.producoes[nt] = []

        # Itera sobre producoes sem recursao direta
        for producao in producoes_nao_recursivas:
            # Corner case, talvez o & tenha que continuar mas acho que nao (nao tem nao)
            if producao == "&":
                self.producoes[nt].append(Production(novo_simbolo))
                continue

            self.producoes[nt].append(Production(producao+" "+novo_simbolo))

        # Criacao das producoes do novo simbolo TODO: ESSE PRODUCAO AQUI TA SUS
        self.producoes[novo_simbolo] += [Production(" ".join(producao[1:])+" "+novo_simbolo) for producao in producoes_recursivas]

    # Retorna a gramatica sem recursao a esquerda
    def sem_recursao(self):

        # Gramatica e_livre e sem loops :)
        self = self.tratamento_1()

        # Notacao dos slides da professora
        for i, ai in enumerate(self.nao_terminais):

            # Eliminacao da recursao indireta
            for _, aj in zip(range(i), self.nao_terminais):
                for pi in self.producoes[ai]:
                    if pi[0] == aj:
                        for pj in self.producoes[aj]:
                            if pj != "&":
                                self.producoes[ai].append(Production((pj+" "+" ".join(pi[1:])).strip()))
                            else:
                                self.producoes[ai].append(Production(" ".join(pi[1:])))
                        self.producoes[ai].remove(pi)

            def tratamento_improvisado(nt):
                # Eliminacao de loops e producoes unitarias criadas
                for producao in self.producoes[nt]:
                    if len(producao) == 1 and producao in self.nao_terminais:
                        if producao == nt:
                            self.producoes[nt].remove(producao)
                        else:
                            self.herdar_primeiro(nt, producao)

            # Eliminacao da recursao direta
            # tratamento_improvisado(ai)
            self.eliminar_recursao_direta(ai)
            # tratamento_improvisado(ai)

        self.to_file("debug/sem_recursao")
        return self

    ######################## Fatoracao ########################

    # (Recursiva) Retorna se ha ou nao nd_indireto neste nao terminal
    def ha_nd_indireto(self, nt, derivaveis = None):
        # Cria o conjunto de simbolos derivaveis caso necessario
        if derivaveis == None:
            derivaveis = set()
        derivaveis.add(nt)

        # Olha todos os simbolos da producao
        for producao in self.producoes[nt]:
            # Se o simbolo da producao ja foi encontrado como derivavel
            if producao[0] == nt:
                return True
                raise RuntimeError("RECURSAO DIRETA QUANDO NAO ERA PRA TER HEIN")

            # Itera sobre os simbolos da producao (podem ser anulaveis)
            anulaveis = self.anulaveis()
            for simbolo in producao:

                # Guarda
                if simbolo == "&":
                    continue

                # Simbolo repetido, implica recursao indireta
                if simbolo in derivaveis:
                    return True

                # Terminal novo, nao eh anulavel, bola pra frente
                if simbolo in self.terminais:
                    derivaveis.add(simbolo)
                    break

                # Nao terminal novo
                elif simbolo in self.nao_terminais:

                    # Tem que ver se de fato nao tem nao determinismo
                    if self.ha_nd_indireto(simbolo, derivaveis): #(A funcao o coloca no conjunto de derivaveis)
                        return True

                    # Se o simbolo nao eh anulavel nao tem que ver os proximos, se eh tem
                    # (Nota que na chamada de funcao o nt chamado ja se colocou no conjunto)
                    if not simbolo in anulaveis:
                        break
                
                else: raise RuntimeError(f"Simbolo {simbolo} nao eh terminal ou nao-terminal ????")

        return False

    # Altera a gramatica para retirar nao determinismo direto
    def eliminar_nd_direto(self, nao_terminal: str):
        houve_alteracao = True
        novos_nt = []
        simbolos_tratados = set()
        # Elimina quantos nao determinismos diretos forem necessarios
        while houve_alteracao:

            # Cria uma lista de simbolos inciais
            houve_alteracao = False
            simbolos_iniciais = [producao[0] for producao in self.producoes[nao_terminal]]

            for simbolo_nd in simbolos_iniciais:
                # ha nao determinismo com este simbolo
                if simbolos_iniciais.count(simbolo_nd) > 1 and not simbolo_nd in simbolos_tratados:
                    simbolos_tratados.add(simbolo_nd)
                    houve_alteracao = True

                    # Separa os indices das producoes que sao repetidas
                    producoes_nd = [producao for producao in self.producoes[nao_terminal] if producao[0] == simbolo_nd]
                    
                    # Elimina as producoes nao deterministicas
                    for producao in producoes_nd:
                        self.producoes[nao_terminal].remove(producao)

                    # Cria um novo nao terminal que produz dos nao deterministicos
                    novo_nt = self.novo_nao_terminal(nao_terminal)
                    novos_nt.append(novo_nt)

                    # Cria as producoes do novo nao terminal
                    self.producoes[novo_nt] = [Production(" ".join(producao[1:])) for producao in producoes_nd]

                    # Edge case onde o simbolo nao terminal era uma producao unica
                    for producao in self.producoes[novo_nt]:
                        if producao == "":
                            self.producoes[novo_nt].remove("")
                            self.producoes[novo_nt].append(Production("&"))

                    # Transicao que leva pro novo nao terminal
                    self.producoes[nao_terminal].append(Production(simbolo_nd+" "+novo_nt))

                    break

        return novos_nt

    # Monta a arvore de derivacores da gramatica
    def eliminar_nd_indireto(self, nao_terminal: str):
        # print(f"tratando {len(self.producoes)}")
        alterations = True
        self.eliminar_nd_direto(nao_terminal)
        self.to_file("error_grammar")
        while alterations:
            alterations = False
            anulaveis = self.anulaveis()
            arvore =  ArvoreAuxiliar(self, nao_terminal, anulaveis)
            if not arvore.nd:
                return
            for simbolo in set(arvore.folhas_simbolos):
                # Nao precisamos tratar
                caminho_comum, caminhos = arvore.ancestral_comum_derivativo(simbolo)
                # Se aquele simbolo nao causa nao determinismo nao o tratamos
                if caminho_comum is None: continue

                alterations = True
                # print(simbolo, caminho_comum, caminhos)
                for caminho in caminhos:
                    for nodo in caminho:
                        if nodo.folha: break
                        if nodo.simbolo == "&":
                            print(f"comum: {caminho_comum} caminho: {caminho}")
                        self.herdar_primeiro(caminho_comum[-1].simbolo, nodo.simbolo)
                self.eliminar_nd_direto(caminho_comum[-1].simbolo)
                self.sem_repeticoes()
    
    # Retira o nd direto da gramatica toda
    def sem_nd_direto(self):
        houve_alteracao = True
        while houve_alteracao:
            antes = len(self.nao_terminais)
            for nao_terminal in self.nao_terminais:
                self.eliminar_nd_direto(nao_terminal)
            depois = len(self.nao_terminais)
            houve_alteracao = antes != depois
            self.sem_diretas().sem_repeticoes()
        return self
    
    # Retorna a gramatica fatorada (Codigo ta um lixo mas funciona)
    def fatorada(self):

        self.sem_nd_direto()
        self.pretify()
        
        self.to_file("debug/grammar_sem_nd_direto")

        for nao_terminal in self.nao_terminais:
            self.eliminar_nd_indireto(nao_terminal)

        return self

        # self.to_file("lixo.txt")
        # print(self)

        # TODO: POSSIVEL PROBLEMA PRA GRAMATICAS COMPLEXAS
        # nts = list(self.producoes.keys())

        # for nao_terminal in nts:
        #     # print("-----------")
        #     # print("to limpando:",nao_terminal)
        #     # print(self)

        #     for _ in range(100):
        #         self.sem_repeticoes()
        #         # Guarda p/ crescimento muito grande
        #         self.to_file("error_grammar")
        #         if len(self.producoes[nao_terminal]) > 100 or len(self.producoes) > 300:
        #             raise RuntimeError("Nao consegui fatorar a gramatica (muita producao)")

        #         # TODO: VER SE VALE USAR ISSO OU NAO
        #         # Nao ha nd indireto a ser resolvido
        #         if not self.ha_nd_indireto(nao_terminal):
        #             break

        #         # Itera sobre as producoes herdando todos os iniciais sempre que possivel
        #         for producao in self.producoes[nao_terminal]:
        #             # Comeca de fato com um nao terminal
        #             if producao[0] in self.nao_terminais:
        #                 # print(f"estou herdando {producao[0]}")
        #                 self.herdar_primeiro(nao_terminal, producao[0])
        #                 break
        #         # Se ele nao conseguiu herdar nada
        #         else:
        #             break
        #     # Impede mais que 100 derivacoes sucessivas
        #     else:
        #         raise RuntimeError("Nao consegui fatorar a gramatica (limite de derivacoes)")

        #     # Elimina ND direto gerado
        #     novos_nt = self.eliminar_nd_direto(nao_terminal)
        #     for nt in novos_nt:
        #         nts.append(nt)

        # return self

    # Abreviacao de um monte de coisa
    def tratada(self):
        g = self.sem_recursao()
        g = g.sem_diretas().sem_inalcancaveis().fatorada().sem_diretas().sem_unitarias().pretify()
        g.to_file("debug/grammar_tratada")
        return g

    ################### First e Follow #####################

    # Retorna o firstpos de uma producao
    def first_prod(self, producao: Production):

        if producao == []:
            return {"&"}

        if producao[0] in self.terminais or producao[0] == "&":
            return {producao[0]}

        first = set()
        anulaveis = self.anulaveis()
        # Inclui o firstpost de todos simbolos ate o primeiro nao anulavel
        for simbolo in producao:
            self.__firstpos_simbol(simbolo, first)
            if not simbolo in anulaveis:
                if "&" in first:
                    first.remove("&")
                break
        return first

    # Calcula o firstpos de um nao terminal
    def __firstpos_simbol(self, cabeca: str, first: set = None):

        if first == None:
            first = set()

        def check_nd():
            if cabeca in first:
                raise RuntimeError("Nao determinismo no calculo de Firstpos")

        # o first de um terminal eh o proprio terminal
        if cabeca in self.terminais or cabeca == "&":
            check_nd()
            first.add(cabeca)
            return first

        anulaveis = self.anulaveis()
        # Itera sobre as producoes do nao terminal
        for producao in self.producoes[cabeca]:

            # Itera sobre os simbolos de uma producao
            for simbolo in producao:

                # Se o simbolo da producao eh um terminal
                if simbolo in self.terminais or simbolo == "&":
                    check_nd()
                    first.add(simbolo)
                    break

                # Simbolo nao terminal
                self.__firstpos_simbol(simbolo, first)

                # Simbolo nao anulavel
                if not simbolo in anulaveis:
                    break
            else:
                # Producao inteira anulaves
                first.add("&")

        return first
    
    # Calcula o firstpos da gramatica
    def firspost(self):
        first = {nt:[] for nt in self.nao_terminais}
        for nt in self.nao_terminais:
            first[nt] = self.__firstpos_simbol(nt)
        return first
    
    # Calcula o followpos de um nao terminal
    def __followpos_nt(self, nt: str, analisys_set = None):

        if analisys_set is None:
            analisys_set = set()

        analisys_set.add(nt)
        # Memoizacao do problema
        if nt in self.follow.keys():
            return self.follow[nt]
        
        follow = set()
        anulaveis = self.anulaveis()

        # Fim de arquivo sempre ao fim do simbolo inicial
        if nt is self.inicial:
            follow.add("$")

        # Itera sobre as producoes
        for nt_analisado, producoes in self.producoes.items():
            for producao in producoes:

                # Encontra o simbolo em outras producoes
                for i, simbolo in enumerate(producao):
                    if nt != simbolo: continue

                    # Firstpos de tudo que vem depois dele
                    post = self.first_prod(producao[i+1:])

                    # Firstpos do resto da producao nao eh literalmente so &
                    if {'&'} != post:
                        if '&' in post:
                            follow = follow.union(post-{'&'})
                        else:
                            follow = follow.union(post)
                    self.follow[nt] = follow

                    # Firstpos do resto da producao anulavel
                    if self.nullable_sentence(post, anulaveis):
                        if not nt_analisado in self.follow.keys():
                            if not nt_analisado in analisys_set.copy():
                                follow = follow.union(self.__followpos_nt(nt_analisado, analisys_set.copy()))
                        else:
                            follow = follow.union(self.follow[nt_analisado])

        self.follow[nt] = follow
        return follow

    # Calcula o followpos da gramatica
    def followpost(self):
        self.follow = {}
        for i, nt in enumerate(self.nao_terminais):
            # print(i, len(self.nao_terminais), nt)
            self.__followpos_nt(nt)
        return self.follow

if __name__ == "__main__":
    arquivo = "grammar"
    path = "compiladores/"
    g = Gramatica().from_file_preprocess(path+arquivo).tratada()
    g.to_file(path+arquivo+"_tratada")