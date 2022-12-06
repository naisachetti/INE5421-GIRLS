import string
import sys
from ArvoreSintatica import *
from Pilha import *

class Automato:

    # Cria o automato
    def __init__(self) -> None:
        
        # Cria um automato vazio se nao receber arquivo
        self.estados = None
        self.n_estados = None
        self.finais = None
        self.inicial = None
        self.alfabeto = None
    
    # Cria o automato a partir de um arquivo contendo uma regex
    def from_regex(self, filename: str):
        # Instanciacao de uma Arvore Sintatica para a regex
        regex = self.read_regex(filename)
        print(regex)
        a_sint = ArvoreSintatica(regex)

        # Definicao dos estados e suas transicoes
        (self.estados, estado_inicial) = a_sint.get_estados_automato()

        # Definicao da quantidade de estados no automato
        self.n_estados = len(self.estados)-1

        # Definicao dos estados finais
        self.finais: list = []
        for estado in self.estados:
            if estado["final"]:
                self.finais.append(estado["nome"])
        
        # Definicao do estado inicial
        self.inicial = estado_inicial

        # Definicao do alfabeto
        self.alfabeto = a_sint.get_alfabeto()

        return self

    # Le a regex e definicoes regulares a partir de um arquivo.
    # Retorna a mesma regex sem definicoes regulares (ou seja, com as definicoes regulares ja substituidas em si).
    def read_regex(self, filename):
        letras = list(string.ascii_lowercase)
        regdefs:dict[str, str] = {}
        regex = ""

        # Leitura da regex e definicoes regulares
        with open(filename, "r") as arquivo:
            while True:
                linha = arquivo.readline()
                if linha[0] not in ['#'] and len(linha) > 1:
                    # Se é uma definicao regular
                    if linha[0] not in ['>']:
                        # Verifica se a definicao regular comeca com uma letra e nao eh nomeada com apenas uma letra
                        if linha[0] in letras:
                            buffer = ""
                            for char in linha:
                                if char != ':':
                                    buffer += char
                                else:
                                    if len(buffer) > 1:
                                        regdef = linha[len(buffer)+1 : len(linha)-1]
                                        regdefs[buffer] = regdef
                                    else:
                                        raise Exception("Definição regular com formato incorreto. Não deve ser nomeada com apenas uma letra.")
                        else:
                            raise Exception("Definição regular com formato incorreto. Deve começar com letra.")
                    # Se nao eh uma definicao regular, mas sim uma ER
                    else:
                        buffer = ""
                        for char in linha:
                            if char == '>':
                                pass
                            elif char != ':':
                                buffer += char
                            else:
                                if len(buffer) > 1:
                                    regex = linha[len(buffer)+2 : len(linha)]
                                else:
                                    raise Exception("Definição regular com formato incorreto. Não deve ser nomeada com apenas uma letra.")
                        break
        
        new_regex = regex+" "

        # Substituicao das definicoes regulares dentro da regex.
        # Substitui todas as definicoes regulares que forem possiveis em uma passada
        # pela regex e, caso substituicoes tenham sido realmente feitas, analisa a nova regex.
        # Este processo se repete ate que nao haja mais definicoes regulares na regex.
        while True:
            regex = new_regex
            buffer = ""
            index_i = 0
            inc_i = 0
            for i in range (len(regex)):
                if (new_regex[i+inc_i] in ['(',')','.','+','*','|','?',' ']) or (i == len(regex)-1):
                    if (len(buffer) > 1) and (buffer in regdefs.keys()):
                        new_regex = new_regex[0:index_i] + '(' + regdefs[buffer] + ')' + new_regex[i+inc_i:len(new_regex)]
                        inc_i += len(regdefs[buffer])-len(buffer)-1
                        buffer = ""
                    else:
                        buffer = ""
                else:
                    if len(buffer) == 0:
                        index_i = i+inc_i
                    buffer += new_regex[i+inc_i]

            if new_regex == regex:
                break

        # Adicao de sequencias de numeros ou letras do tipo [A-Za-z] e [0-9]
        inc_i = 0
        init_i = 0
        new_regex = regex
        for i in range (len(regex)):
            if new_regex[i+inc_i] == '[':
                seq_add = ""
                index_init = i+inc_i
                init_i = i+inc_i
                while new_regex[init_i+1] != ']':
                    seq_init = new_regex[init_i+1]
                    seq_end = new_regex[init_i+3] # Motivo da verificação "if init_i+3 >= len(new_regex)"

                    caracteres = []
                    if seq_init.isupper() and seq_end.isupper() and seq_init < seq_end:
                        caracteres = list(string.ascii_uppercase)
                    elif  seq_init.islower() and seq_end.islower() and seq_init < seq_end:
                        caracteres = list(string.ascii_lowercase)
                    elif seq_init.isdigit() and seq_end.isdigit() and seq_init < seq_end:
                        caracteres = list(string.digits)
                    else:
                        raise Exception("Erro. Regex mal formada. Sequência de letras ou dígitos inválida.")

                    if len(seq_add) > 0:
                        seq_add += '|('
                    else:
                        seq_add += '('
                    for char in caracteres:
                        if char >= seq_init and char <= seq_end:
                            seq_add += char+'|'
                    seq_add = seq_add[:-1]
                    seq_add += ')'

                    init_i += 3
                    if (init_i+3) >= len(new_regex): 
                        raise Exception("Erro. Regex mal formada. Sequência de letras ou dígitos inválida.")

                seq_add = '(' + seq_add + ')'
                
                index_end = init_i+1
                new_regex = new_regex[0:index_init] + seq_add + new_regex[index_end+1:len(new_regex)]
                inc_i += len(seq_add)-(index_end-index_init)-1

        regex = new_regex

        # Adicao de concatenacoes implicitas
        inc_i = 0
        new_regex = regex
        for i in range (len(regex)):
            if new_regex[i+inc_i] not in [')','.','+','*','|','?',' ']:
                k = i+inc_i-1
                while (k >= 0) and new_regex[k] == ' ':
                    k -= 1
                if (k >= 0) and (new_regex[k] not in ['(','.','|']):
                    new_regex = new_regex[0:k+1] + '.' + new_regex[k+1:len(new_regex)]
                    inc_i += 1

        regex = new_regex

        # Transformacao da regex em notacao infixada para notacao prefixada.
        # Algoritmo retirado de: https://www.geeksforgeeks.org/convert-infix-prefix-notation/
        prec_op = {'*':3, '+':3, '?':3, '.':2, '|': 1}
        assoc_op = {'*':"direita,", '+':"direita", '?':"direita", '.':"esquerda", '|':"esquerda"}
        
        # Inverte regex infixada original
        regex_invertida = ""
        aux_regex_invertida = regex[::-1]
        for char in aux_regex_invertida:
            if char == '(':
                regex_invertida += ')'
            elif char == ')':
                regex_invertida += '('
            else:
                regex_invertida += char

        # Converte regex infixada invertida para uma regex posfixada
        operadores = Pilha()
        regex_inv_posf = ""
        for char in regex_invertida:
            if char not in ['(',')','*','+','?','.','|',' ']:
                regex_inv_posf += char
            elif char == ' ':
                pass
            elif char == '(':
                operadores.push('(')
            elif char == ')':
                operador = operadores.pop()
                while operador != '(':
                    regex_inv_posf += operador
                    operador = operadores.pop()
            else:
                if operadores.size() == 0 or operadores.top() == '(':
                    operadores.push(char)
                else:
                    if char == operadores.top():
                        if assoc_op[char] == "direita":
                            operadores.push()
                        else:
                            regex_inv_posf += operadores.pop()
                            operadores.push(char)
                    else:
                        operador = operadores.top()
                        while (operadores.size() > 0) and (operador != '(') and (prec_op[operador] >= prec_op[char]):
                            regex_inv_posf += operadores.pop()
                            operador = operadores.top()
                        operadores.push(char)

        while operadores.size() > 0:
            regex_inv_posf += operadores.pop()

        # Inverte regex posfixada, obtendo uma regex prefixada da regex infixada original
        regex_pref = regex_inv_posf[::-1]

        return regex_pref

    # Le o automato a partir de um arquivo
    def from_file(self, filename: str):
        self.estados: list[dict] = []
        with open(filename, "r") as arquivo:
            
            # Leitura do cabecalho
            self.n_estados: int = int(arquivo.readline().strip())
            inicial: str = arquivo.readline().strip()
            self.finais: list = arquivo.readline().strip().split(",")
            self.alfabeto: list[str] = arquivo.readline().strip().split(",")
            
            # Criacao do estado morto
            morto: dict = {"nome": "Morto", "final": False}
            for simbolo in self.alfabeto:
                morto[simbolo] = [morto]
            self.estados.append(morto)
            
            # Criacao de todos os estados e suas transicoes
            for line in arquivo:
                # Leitura da linha
                origem, simbolo, destinos = line.strip().split(",")

                if not simbolo in self.alfabeto:
                    raise RuntimeError(f"o simbolo {simbolo} nao pertence ao meu alfabeto mas esta numa transicao")

                destinos = list(destinos.split("-")) # Nao Determinismo

                # Criacao dos estados na tansicao caso eles ainda nao existam
                def novo_estado(nome: str):

                    # Estado eh de fato novo
                    if not nome in [estado["nome"] for estado in self.estados]:
                        estado = {"nome": nome, "final": nome in self.finais}
                        for simbolo in self.alfabeto:
                            estado[simbolo] = [morto]
                        self.estados.append(estado)
                        return estado

                    # Estado nao eh novo
                    return [estado for estado in self.estados if estado["nome"] == nome][0]
                dict_origem = novo_estado(origem)

                # Transicao
                lista_dict_destino = [novo_estado(destino) for destino in destinos]        
                
                # Criacao da transicao
                dict_origem[simbolo] = lista_dict_destino

        # Erro do numero de estados, o -1 eh do morto
        if len(self.estados)-1 != self.n_estados:
            raise RuntimeError(f"Numero de estados informado errado, contei {len(self.estados)-1} e nao {self.n_estados}")

        # Identificacao do estado inicial
        self.inicial = [estado for estado in self.estados if estado["nome"] == inicial][0]
        return self

    # Retorna uma copia do automato
    def copy(self):
        copia = Automato()
        copia.alfabeto = self.alfabeto.copy()
        copia.finais = self.finais.copy()
        copia.n_estados = self.n_estados
        estados_copia = [estado.copy() for estado in self.estados]
        # Ajusta as referencias para que se refiram as copias nao ao original
        for estado_copia in estados_copia:
            for simbolo in copia.alfabeto:
                nova_lista = []
                for estado in estado_copia[simbolo]:
                    nova_lista += [e for e in estados_copia if estado["nome"] == e["nome"]]
                estado_copia[simbolo] = nova_lista
        copia.estados = estados_copia
        copia.inicial = [estado for estado in estados_copia if estado["nome"] == self.inicial["nome"]][0]
        return copia

    # Representacao do automato ao ser impresso
    def __repr__(self) -> str:
        saida = f"n estados: {self.n_estados}\n"
        saida += f"estado inicial: "+self.inicial["nome"]+"\n"
        saida += f"estados finais: "+",".join(self.finais)+"\n"
        saida += f"alfabeto: "+",".join(self.alfabeto)+"\n"
        for estado in self.estados:
            if estado["nome"] == "Morto": continue
            for simbolo in self.alfabeto:
                if estado[simbolo][0]["nome"] == "Morto": continue
                saida += estado["nome"]+": "+simbolo+" -> "
                saida += "-".join([est["nome"] for est in estado[simbolo]])+"\n"
        return saida
 
    # Recebe uma entrada e retorna se o automato a reconhece
    # SE RECEBER UM AFND VAI DAR PAU
    def reconhece(self, entrada: str) -> bool:
        estado_atual = self.inicial
        for simbolo in entrada:
            if len(estado_atual[simbolo]) > 1:
                nome_str = "nome"
                raise RuntimeError(f"Tansicao nao deterministica de {estado_atual[nome_str]} por {simbolo}")
            elif len(estado_atual[simbolo]) == 0:
                nome_str = "nome"
                raise RuntimeError(f"Tansicao de {estado_atual[nome_str]} por {simbolo} NAO EXISTE (???)")
            
            estado_atual = estado_atual[simbolo][0]
        return estado_atual["final"]
    
    # Recebe outro automato e retorna a uniao entre os dois
    def uniao_com(self, other):
        uniao = Automato()
        copia = self.copy()
        other = other.copy()

        uniao.n_estados = copia.n_estados + other.n_estados + 1

        # Identifica o estado morto da copia e do outro e transfere o do outro para o da copia
        morto_copia = [estado for estado in copia.estados if estado["nome"] == "Morto"][0]
        morto_other = [estado for estado in other.estados if estado["nome"] == "Morto"][0]
        for estado in other.estados:
            for simbolo in other.alfabeto:
                if estado[simbolo][0]["nome"] == "Morto":
                    estado[simbolo] = [morto_copia]
        other.estados.remove(morto_other)
        
        # Cria o novo alfabeto e inclui &
        uniao.alfabeto = list(dict.fromkeys(copia.alfabeto+other.alfabeto+["&"]))
        
        # Cria transicoes vazias nos automatos que serao unidos para os simbolos especificados
        def transicao_vazia(automato, alfabeto):
            for simbolo in alfabeto:
                if not simbolo in automato.alfabeto:
                    for estado in automato.estados:
                        estado[simbolo] = [morto_copia]
        transicao_vazia(copia, uniao.alfabeto)
        transicao_vazia(other, uniao.alfabeto)

        # Muda o nome dos estados do outro automato
        for estado in other.estados:
            estado["nome"] += "_"
        other.finais = [outro + "_" for outro in other.finais]
        uniao.finais = copia.finais + other.finais

        # Cria o estado inicial que vai por epslon para os outros iniciais e pra nenhum mais
        uniao.inicial = {"nome": "inicio_uniao", "final": False, "&": [copia.inicial, other.inicial]}
        for simbolo in uniao.alfabeto:
            if simbolo == "&":
                continue
            uniao.inicial[simbolo] = [morto_copia]

        # Une de fato os estados
        uniao.estados = [uniao.inicial] + copia.estados + other.estados
        
        return uniao

    # Exporta o arquivo do automato
    def to_file(self, filename: str):
        with open(filename, "w") as arquivo:
            arquivo.write(f"{self.n_estados}\n")
            arquivo.write(self.inicial["nome"]+"\n")
            arquivo.write(",".join(self.finais)+"\n")
            arquivo.write(",".join(self.alfabeto)+"\n")
            for estado in self.estados:
                if estado["nome"] != "Morto":
                    for simbolo in self.alfabeto:
                        if estado[simbolo][0]["nome"] != "Morto":
                            arquivo.write(estado["nome"]+","+simbolo+",")
                            arquivo.write("-".join([est["nome"] for est in estado[simbolo]])+"\n")

    # Renomea os estados do automato
    def rename(self):

        # Gerador de nomes
        def nomes():
            num = 0
            while True:
                yield "q"+str(num)
                num += 1
        gerador = nomes()

        # Renomeia os estados
        self.finais = []
        for estado in self.estados:
            if estado["nome"] != "Morto":
                estado["nome"] = next(gerador)
                if estado["final"]:
                    self.finais.append(estado["nome"])
        
        return self

    # Retorna uma versao determinizada do automato
    def determinizado(self):
        copia = self.copy()

        # Identificacao do &-fecho dos estados (lista)
        for estado in copia.estados:
            estado["fecho"] = [estado]
            estado["fecho"] += [fecho for fecho in estado["&"] if fecho["nome"] != "Morto"]
        
        # Retorna o nome dos estados aglutinados
        def aglutinar_nome(estados: list):
            return "+".join([estado["nome"] for estado in estados])
        
        # Todos os estados do determinizado sao listas antes de serem ajustados
        determinizado = Automato()
        determinizado.finais = []
        determinizado.n_estados = 1

        # Alfabeto do automato determinizado
        determinizado.alfabeto = copia.alfabeto
        determinizado.alfabeto.remove("&")

        # Criacao do estado morto
        morto: dict = {"nome": "Morto", "final": False}
        for simbolo in determinizado.alfabeto:
            morto[simbolo] = [morto]
        
        # Estados fundamentais
        determinizado.inicial = {"nome": aglutinar_nome(copia.inicial["fecho"]), "fecho": copia.inicial["fecho"]}
        determinizado.inicial["final"] = True in [estado["final"] for estado in determinizado.inicial["fecho"]]
        if determinizado.inicial["final"]:
            determinizado.finais.append(determinizado.inicial["nome"])
        determinizado.estados = [morto, determinizado.inicial]

        # Retorna o estado determinizado equivalente a transicao ND
        def destino_deterministico(estados: list, simbolo: str):
            estados_destino = []
            for estado in estados:
                for estado_destino in estado[simbolo]:
                    if estado_destino not in estados_destino and estado_destino["nome"] != "Morto":
                        estados_destino.append(estado_destino)
            
            # Nao ha transicao, retorna o morto
            if estados_destino == []:
                return [estado for estado in determinizado.estados if estado["nome"] == "Morto"][0]
            
            # Gera o estado determinizado
            estado_determinizado =\
                    {"nome": aglutinar_nome(estados_destino), 
                    "final": False, 
                    "fecho": estados_destino}

            for estado in determinizado.estados:
                # ESTADO JA EXISTIA
                if estado["nome"] == estado_determinizado["nome"]:
                    return estado
            
            # ESTADO NAO EXISTIA

            # Verifica se este estado eh de aceitacao e acrescenta nos finais se for o caso
            for estado in estados_destino:
                if estado["final"] == True:
                    estado_determinizado["final"] = True

            if estado_determinizado["final"]:
                determinizado.finais.append(estado_determinizado["nome"])

            determinizado.n_estados += 1

            determinizado.estados.append(estado_determinizado)
            return estado_determinizado

        # Estados do automato determinizado
        for estado in determinizado.estados:
            if estado["nome"] == "Morto": continue
            for simbolo in determinizado.alfabeto:
                estado[simbolo] = [destino_deterministico(estado["fecho"], simbolo)]

        return determinizado


# epico = Automato().from_regex("regex_exemplo4.txt")
# Automato().from_file("automato_exemplo.txt").to_file("veremos.txt")
# a = Automato().from_file("unido_a.txt")
# while True:
#     entrada = input()
#     if entrada == "stop":
#         break
#     else:
#         print(a.reconhece(entrada))
# b = Automato().from_file("unido_b.txt")
# v = Automato().from_file("determinizado.txt")
# ab = a.uniao_com(b).uniao_com(v).determinizado().rename()
# ab.to_file("epico.txt")
# Automato().from_regex("regex_exemplo.txt").to_file("from_regex_exemplo.txt")
# Automato().from_regex("regex_exemplo2.txt").to_file("from_regex_exemplo2.txt")
# Automato().from_regex("regex_exemplo3.txt").to_file("from_regex_exemplo3.txt")
Automato().from_regex("regex_exemplo4.txt").to_file("from_regex_exemplo4.txt")
# Automato().from_regex("regex_exemplo5.txt").to_file("from_regex_exemplo5.txt")
# Automato().from_regex("regex_exemplo6.txt").to_file("from_regex_exemplo6.txt")
# Automato().from_regex("regex_exemplo7.txt").to_file("from_regex_exemplo7.txt")
