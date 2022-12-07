from ArvoreSintatica import *
from Pilha import *
from regex_lib import read_regex

class Automato:

    # Cria o automato
    def __init__(self) -> None:

        # Cria um automato vazio se nao receber arquivo
        self.estados = None
        self.n_estados = None
        self.finais = None
        self.inicial = None
        self.alfabeto = None

    # Cria o automato a partir de um arquivo contendo uma ou multiplas regex
    def from_regex(self, regex, token_type):
        # Instanciacao de uma Arvore Sintatica para a regex
        a_sint = ArvoreSintatica(regex)

        # Definicao dos estados e suas transicoes
        (self.estados, estado_inicial) = a_sint.get_estados_automato()

        # Definicao da quantidade de estados no automato
        self.n_estados = len(self.estados)-1

        # Definicao dos estados finais
        self.finais: list = []
        for estado in self.estados:
            if estado["final"]:
                estado["token"] = [token_type]
                self.finais.append(estado["nome"])

        # Definicao do estado inicial
        self.inicial = estado_inicial

        # Definicao do alfabeto
        self.alfabeto = a_sint.get_alfabeto()

        return self

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
        saida += f"estados finais: \n"
        saida += "".join([estado["nome"] + " representando " + estado["token"][0] + "\n" for estado in self.estados if estado["final"]])
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
    def percorre(self, entrada: str) -> dict:
        estado_atual = self.inicial
        for simbolo in entrada:
            if len(estado_atual[simbolo]) > 1:
                nome_str = "nome"
                raise RuntimeError(f"Tansicao nao deterministica de {estado_atual[nome_str]} por {simbolo}")
            elif len(estado_atual[simbolo]) == 0:
                nome_str = "nome"
                raise RuntimeError(f"Tansicao de {estado_atual[nome_str]} por {simbolo} NAO EXISTE (???)")

            estado_atual = estado_atual[simbolo][0]
        return estado_atual

    def token(self, entrada: str) -> str:
        return self.percorre(entrada)["token"][0]

    def reconhece(self, entrada: str) -> bool:
        return self.percorre(entrada)["final"]

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

        return uniao.determinizado().rename()

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
        determinizado.inicial = {"nome": aglutinar_nome(copia.inicial["fecho"]), "fecho": copia.inicial["fecho"], "token": []}
        determinizado.inicial["final"] = True in [estado["final"] for estado in determinizado.inicial["fecho"]]
        if determinizado.inicial["final"]:
            determinizado.inicial["token"] = [token for token in estado["token"] for estado in determinizado.inicial["fecho"] if estado["final"]]
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
                    "fecho": estados_destino,
                    "token": [] }

            for estado in determinizado.estados:
                # ESTADO JA EXISTIA
                if estado["nome"] == estado_determinizado["nome"]:
                    return estado

            # ESTADO NAO EXISTIA

            # Verifica se este estado eh de aceitacao e acrescenta nos finais se for o caso
            for estado in estados_destino:
                if estado["final"] == True:
                    estado_determinizado["token"] += estado["token"]
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

if __name__ == '__main__':
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
    # # # ab.to_file("epico.txt")
    # regex_exemplo = read_regex("regex_exemplo.txt")
    # Automato().from_regex(regex_exemplo[list(regex_exemplo.keys())[0]], list(regex_exemplo.keys())[0]).to_file("from_regex_exemplo.txt")
    # regex_exemplo2 = read_regex("regex_exemplo2.txt")
    # Automato().from_regex(regex_exemplo2[list(regex_exemplo2.keys())[0]], list(regex_exemplo2.keys())[0]).to_file("from_regex_exemplo2.txt")
    # regex_exemplo3 = read_regex("regex_exemplo3.txt")
    # Automato().from_regex(regex_exemplo3[list(regex_exemplo3.keys())[0]], list(regex_exemplo3.keys())[0]).to_file("from_regex_exemplo3.txt")
    # regex_exemplo4 = read_regex("regex_exemplo4.txt")
    # Automato().from_regex(regex_exemplo4[list(regex_exemplo4.keys())[0]], list(regex_exemplo4.keys())[0]).to_file("from_regex_exemplo4.txt")
    # regex_exemplo5 = read_regex("regex_exemplo5.txt")
    # Automato().from_regex(regex_exemplo5[list(regex_exemplo5.keys())[0]], list(regex_exemplo5.keys())[0]).to_file("from_regex_exemplo5.txt")
    # regex_exemplo6 = read_regex("regex_exemplo6.txt")
    # Automato().from_regex(regex_exemplo6[list(regex_exemplo6.keys())[0]], list(regex_exemplo6.keys())[0]).to_file("from_regex_exemplo6.txt")
    # regex_exemplo7 = read_regex("regex_exemplo7.txt")
    # Automato().from_regex(regex_exemplo7[list(regex_exemplo7.keys())[0]], list(regex_exemplo7.keys())[0]).to_file("from_regex_exemplo7.txt")
    regex_exemplo8 = read_regex("regex_exemplo8.txt")
    Automato().from_regex(regex_exemplo8[list(regex_exemplo8.keys())[0]], list(regex_exemplo8.keys())[0]).to_file("from_regex_exemplo8.txt")
    regex_exemplo9 = read_regex("regex_exemplo9.txt")
    Automato().from_regex(regex_exemplo9[list(regex_exemplo9.keys())[0]], list(regex_exemplo9.keys())[0]).to_file("from_regex_exemplo9.txt")

    regex_exemplo10 = read_regex("regex_exemplo10.txt")
    for nome_regex in regex_exemplo10.keys():
        Automato().from_regex(regex_exemplo10[nome_regex], nome_regex).to_file(("from_regex_exemplo10_"+nome_regex+".txt"))
